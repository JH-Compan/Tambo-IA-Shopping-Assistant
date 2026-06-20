create extension if not exists pgcrypto;

create or replace function public.create_order_transaction(
    p_user_id text,
    p_conversation_id text,
    p_items jsonb
)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
    v_order_id text := pg_catalog.gen_random_uuid()::text;
    v_order_item_id text;
    v_interaction_id text;
    v_total_amount numeric := 0;
    v_items_count integer := 0;
    v_item jsonb;
    v_item_id text;
    v_item_type text;
    v_quantity integer;
    v_unit_price numeric;
    v_subtotal numeric;
    v_product record;
    v_promotion record;
    v_promotion_item record;
    v_required_stock integer;
    v_purchased_promo_qty integer;
begin
    if p_user_id is null or btrim(p_user_id) = '' then
        raise exception 'VALIDATION: user_id es obligatorio';
    end if;

    if not exists (
        select 1
        from public.chat_users
        where id = p_user_id
          and is_active = true
    ) then
        raise exception 'VALIDATION: El usuario no existe o está inactivo';
    end if;

    if p_items is null
       or jsonb_typeof(p_items) <> 'array'
       or jsonb_array_length(p_items) = 0 then
        raise exception 'VALIDATION: El carrito está vacío';
    end if;

    if p_conversation_id is not null
       and btrim(p_conversation_id) <> '' then

        if not exists (
            select 1
            from public.chat_conversations
            where id = p_conversation_id
              and user_id = p_user_id
        ) then
            raise exception
                'VALIDATION: La conversación no existe o no pertenece al usuario';
        end if;
    else
        p_conversation_id := null;
    end if;

    insert into public.sales_orders (
        id,
        user_id,
        conversation_id,
        order_date,
        total_amount,
        status
    )
    values (
        v_order_id,
        p_user_id,
        p_conversation_id,
        now(),
        0,
        'completed'
    );

    for v_item in
        select value
        from jsonb_array_elements(p_items)
    loop
        v_item_id := nullif(btrim(v_item->>'item_id'), '');
        v_item_type := lower(
            btrim(coalesce(v_item->>'item_type', ''))
        );

        begin
            v_quantity := (v_item->>'quantity')::integer;
        exception
            when invalid_text_representation then
                raise exception
                    'VALIDATION: La cantidad del item % debe ser un número entero',
                    coalesce(v_item_id, 'sin identificador');
        end;

        if v_item_id is null then
            raise exception
                'VALIDATION: Cada item debe incluir item_id';
        end if;

        if v_item_type = 'producto' then
            v_item_type := 'product';
        elsif v_item_type in ('promocion', 'promoción') then
            v_item_type := 'promotion';
        end if;

        if v_item_type not in ('product', 'promotion') then
            raise exception
                'VALIDATION: item_type inválido para %',
                v_item_id;
        end if;

        if v_quantity is null or v_quantity < 1 then
            raise exception
                'VALIDATION: La cantidad debe ser mayor o igual a 1 para %',
                v_item_id;
        end if;

        /*
         * COMPRA DE PRODUCTO INDIVIDUAL
         */
        if v_item_type = 'product' then
            select
                id,
                price,
                stock,
                is_active
            into v_product
            from public.cat_products
            where id = v_item_id
            for update;

            if not found then
                raise exception
                    'VALIDATION: El producto % no existe',
                    v_item_id;
            end if;

            if coalesce(v_product.is_active, false) = false then
                raise exception
                    'VALIDATION: El producto % no está activo',
                    v_item_id;
            end if;

            if coalesce(v_product.stock, 0) < v_quantity then
                raise exception
                    'STOCK: Stock insuficiente para el producto %. Disponible: %, solicitado: %',
                    v_item_id,
                    coalesce(v_product.stock, 0),
                    v_quantity;
            end if;

            v_unit_price := coalesce(v_product.price, 0);
            v_subtotal := v_unit_price * v_quantity;

            update public.cat_products
            set
                stock = stock - v_quantity,
                updated_at = now(),
                is_active = case
                    when stock - v_quantity = 0 then false
                    else is_active
                end
            where id = v_item_id;

            v_order_item_id := pg_catalog.gen_random_uuid()::text;

            insert into public.sales_order_items (
                id,
                order_id,
                item_type,
                product_id,
                promotion_id,
                quantity,
                unit_price,
                subtotal
            )
            values (
                v_order_item_id,
                v_order_id,
                'product',
                v_item_id,
                null,
                v_quantity,
                v_unit_price,
                v_subtotal
            );

            v_interaction_id := pg_catalog.gen_random_uuid()::text;

            insert into public.ai_user_interactions (
                id,
                user_id,
                conversation_id,
                interaction_type,
                product_id,
                promotion_id,
                weight
            )
            values (
                v_interaction_id,
                p_user_id,
                p_conversation_id,
                'purchased',
                v_item_id,
                null,
                1
            );

        /*
         * COMPRA DE PROMOCIÓN
         */
        else
            select
                id,
                promo_price,
                start_date,
                end_date,
                max_per_customer,
                is_active
            into v_promotion
            from public.cat_promotions
            where id = v_item_id;

            if not found then
                raise exception
                    'VALIDATION: La promoción % no existe',
                    v_item_id;
            end if;

            if coalesce(v_promotion.is_active, false) = false then
                raise exception
                    'VALIDATION: La promoción % no está activa',
                    v_item_id;
            end if;

            if v_promotion.start_date is not null
               and current_date < v_promotion.start_date then
                raise exception
                    'VALIDATION: La promoción % todavía no está vigente',
                    v_item_id;
            end if;

            if v_promotion.end_date is not null
               and current_date > v_promotion.end_date then
                raise exception
                    'VALIDATION: La promoción % ya venció',
                    v_item_id;
            end if;

            if v_promotion.max_per_customer is not null then
                select coalesce(sum(soi.quantity), 0)
                into v_purchased_promo_qty
                from public.sales_order_items soi
                join public.sales_orders so
                  on so.id = soi.order_id
                where so.user_id = p_user_id
                  and soi.promotion_id = v_item_id
                  and so.status = 'completed';

                if v_purchased_promo_qty + v_quantity
                   > v_promotion.max_per_customer then
                    raise exception
                        'VALIDATION: La promoción % excede el máximo por cliente',
                        v_item_id;
                end if;
            end if;

            if not exists (
                select 1
                from public.cat_promotion_items
                where promotion_id = v_item_id
            ) then
                raise exception
                    'VALIDATION: La promoción % no tiene productos asociados',
                    v_item_id;
            end if;

            /*
             * Primero valida y bloquea todo el stock necesario.
             */
            for v_promotion_item in
                select
                    cpi.product_id,
                    cpi.quantity,
                    cpi.is_required
                from public.cat_promotion_items cpi
                where cpi.promotion_id = v_item_id
                order by cpi.product_id
            loop
                if coalesce(v_promotion_item.quantity, 0) < 1 then
                    raise exception
                        'VALIDATION: La promoción % tiene cantidades inválidas',
                        v_item_id;
                end if;

                select
                    id,
                    stock,
                    is_active
                into v_product
                from public.cat_products
                where id = v_promotion_item.product_id
                for update;

                if not found then
                    raise exception
                        'VALIDATION: El producto % de la promoción % no existe',
                        v_promotion_item.product_id,
                        v_item_id;
                end if;

                if coalesce(v_product.is_active, false) = false then
                    raise exception
                        'VALIDATION: El producto % de la promoción % no está activo',
                        v_promotion_item.product_id,
                        v_item_id;
                end if;

                v_required_stock :=
                    v_promotion_item.quantity * v_quantity;

                if coalesce(v_product.stock, 0) < v_required_stock then
                    raise exception
                        'STOCK: Stock insuficiente para la promoción %. Producto: %, disponible: %, requerido: %',
                        v_item_id,
                        v_promotion_item.product_id,
                        coalesce(v_product.stock, 0),
                        v_required_stock;
                end if;
            end loop;

            /*
             * Una vez validado todo, descuenta los productos.
             */
            for v_promotion_item in
                select
                    cpi.product_id,
                    cpi.quantity
                from public.cat_promotion_items cpi
                where cpi.promotion_id = v_item_id
                order by cpi.product_id
            loop
                v_required_stock :=
                    v_promotion_item.quantity * v_quantity;

                update public.cat_products
                set
                    stock = stock - v_required_stock,
                    updated_at = now(),
                    is_active = case
                        when stock - v_required_stock = 0 then false
                        else is_active
                    end
                where id = v_promotion_item.product_id;
            end loop;

            v_unit_price := coalesce(v_promotion.promo_price, 0);
            v_subtotal := v_unit_price * v_quantity;

            v_order_item_id := pg_catalog.gen_random_uuid()::text;

            insert into public.sales_order_items (
                id,
                order_id,
                item_type,
                product_id,
                promotion_id,
                quantity,
                unit_price,
                subtotal
            )
            values (
                v_order_item_id,
                v_order_id,
                'promotion',
                null,
                v_item_id,
                v_quantity,
                v_unit_price,
                v_subtotal
            );

            v_interaction_id := pg_catalog.gen_random_uuid()::text;

            insert into public.ai_user_interactions (
                id,
                user_id,
                conversation_id,
                interaction_type,
                product_id,
                promotion_id,
                weight
            )
            values (
                v_interaction_id,
                p_user_id,
                p_conversation_id,
                'purchased',
                null,
                v_item_id,
                1
            );
        end if;

        v_total_amount := v_total_amount + v_subtotal;
        v_items_count := v_items_count + 1;
    end loop;

    update public.sales_orders
    set
        total_amount = v_total_amount,
        status = 'completed'
    where id = v_order_id;

    return jsonb_build_object(
        'success', true,
        'order_id', v_order_id,
        'total_amount', v_total_amount,
        'items_count', v_items_count
    );
end;
$$;

revoke all
on function public.create_order_transaction(text, text, jsonb)
from public;

revoke all
on function public.create_order_transaction(text, text, jsonb)
from anon;

revoke all
on function public.create_order_transaction(text, text, jsonb)
from authenticated;

grant execute
on function public.create_order_transaction(text, text, jsonb)
to service_role;

