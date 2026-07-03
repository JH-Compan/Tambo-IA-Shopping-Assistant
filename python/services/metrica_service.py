from collections import Counter, defaultdict
from datetime import datetime

from config.supabase_client import supabase


class MetricaService:

    def contar_registros(self, tabla):
        return len(self._table(tabla))

    def obtener_resumen_general(self):
        return {
            "usuarios": self.contar_registros("chat_users"),
            "conversaciones": self.contar_registros("chat_conversations"),
            "mensajes": self.contar_registros("chat_messages"),
            "productos": self.contar_registros("cat_products"),
            "promociones": self.contar_registros("cat_promotions"),
            "pedidos": self.contar_registros("sales_orders"),
            "recomendaciones": self.contar_registros("ai_recommendations"),
            "feedback": self.contar_registros("ai_feedback"),
        }

    def obtener_dashboard_completo(self):
        users = self._table("chat_users")
        conversations = self._table("chat_conversations")
        messages = self._table("chat_messages")
        products = self._table("cat_products")
        categories = self._table("cat_categories")
        promotions = self._table("cat_promotions")
        orders = self._table("sales_orders")
        order_items = self._table("sales_order_items")
        recommendations = self._table("ai_recommendations")
        interactions = self._table("ai_user_interactions")
        feedback = self._table("ai_feedback")

        product_by_id = {row.get("id"): row for row in products if row.get("id")}
        promo_by_id = {row.get("id"): row for row in promotions if row.get("id")}
        category_by_id = {
            row.get("id"): row.get("name") or row.get("nombre") or "Sin categoria"
            for row in categories
            if row.get("id")
        }
        user_by_id = {
            row.get("id") or row.get("user_code"): row
            for row in users
            if row.get("id") or row.get("user_code")
        }

        return {
            "resumen": {
                "usuarios": len(users),
                "conversaciones": len(conversations),
                "mensajes": len(messages),
                "productos": len(products),
                "promociones": len(promotions),
                "pedidos": len(orders),
                "recomendaciones": len(recommendations),
                "feedback": len(feedback),
            },
            "ticket_promedio": self._ticket_promedio(orders),
            "productos_mas_comprados": self._productos_mas_comprados(order_items, product_by_id, promo_by_id),
            "ventas_por_categoria": self._ventas_por_categoria(order_items, product_by_id, promo_by_id, category_by_id),
            "productos_stock_bajo": self._productos_stock_bajo(products),
            "pedidos_por_dia": self._pedidos_por_dia(orders),
            "estado_pedidos": self._estado_pedidos(orders),
            "mensajes_por_dia": self._mensajes_por_dia(messages),
            "intents_frecuentes": self._intents_frecuentes(messages),
            "actividad_por_hora": self._actividad_por_hora(messages),
            "productos_mas_consultados": self._productos_mas_consultados(interactions, product_by_id, promo_by_id),
            "segmentos_usuarios": self._segmentos_usuarios(users),
            "top_clientes": self._top_clientes(orders, user_by_id),
            "funnel_conversion": self._funnel_conversion(conversations, recommendations, orders, feedback),
            "efectividad_recomendaciones": self._efectividad_recomendaciones(recommendations),
            "feedback": self._feedback(feedback),
        }

    def _table(self, table_name):
        try:
            response = supabase.table(table_name).select("*").execute()
            return response.data or []
        except Exception:
            return []

    def _ticket_promedio(self, orders):
        totals = [self._number(row.get("total_amount")) for row in orders]
        total_vendido = sum(totals)
        total_pedidos = len(orders)
        return {
            "total_vendido": round(total_vendido, 2),
            "ticket_promedio": round(total_vendido / total_pedidos, 2) if total_pedidos else 0,
            "pedido_maximo": round(max(totals), 2) if totals else 0,
            "total_pedidos": total_pedidos,
        }

    def _productos_mas_comprados(self, order_items, product_by_id, promo_by_id):
        grouped = {}
        for item in order_items:
            item_id = item.get("product_id") or item.get("promotion_id")
            if not item_id:
                continue
            detail = product_by_id.get(item_id) or promo_by_id.get(item_id) or {}
            name = detail.get("name") or detail.get("title") or detail.get("nombre") or item_id
            quantity = int(self._number(item.get("quantity"), 0))
            subtotal = self._number(item.get("subtotal"))
            if subtotal == 0:
                subtotal = quantity * self._number(item.get("unit_price"))
            record = grouped.setdefault(item_id, {
                "nombre": name,
                "unidades_vendidas": 0,
                "ingresos": 0,
                "stock": detail.get("stock"),
            })
            record["unidades_vendidas"] += quantity
            record["ingresos"] += subtotal
        ranking = sorted(grouped.values(), key=lambda row: row["unidades_vendidas"], reverse=True)
        for row in ranking:
            row["ingresos"] = round(row["ingresos"], 2)
        return ranking[:8]

    def _ventas_por_categoria(self, order_items, product_by_id, promo_by_id, category_by_id):
        grouped = defaultdict(float)
        for item in order_items:
            item_id = item.get("product_id") or item.get("promotion_id")
            detail = product_by_id.get(item_id) or promo_by_id.get(item_id) or {}
            category_id = detail.get("category_id")
            category = category_by_id.get(category_id, detail.get("category_name") or "Sin categoria")
            subtotal = self._number(item.get("subtotal"))
            if subtotal == 0:
                subtotal = self._number(item.get("quantity"), 0) * self._number(item.get("unit_price"))
            grouped[category] += subtotal
        return [
            {"categoria": key, "ingresos": round(value, 2)}
            for key, value in sorted(grouped.items(), key=lambda item: item[1], reverse=True)[:8]
        ]

    def _productos_stock_bajo(self, products, limit=10):
        active = [row for row in products if row.get("is_active", True)]
        low_stock = sorted(
            [row for row in active if self._number(row.get("stock"), 0) <= limit],
            key=lambda row: self._number(row.get("stock"), 0),
        )
        return [
            {
                "id": row.get("id"),
                "name": row.get("name") or row.get("nombre") or "Producto",
                "price": self._number(row.get("price")),
                "stock": int(self._number(row.get("stock"), 0)),
            }
            for row in low_stock[:12]
        ]

    def _pedidos_por_dia(self, orders):
        grouped = defaultdict(lambda: {"pedidos": 0, "monto": 0})
        for row in orders:
            day = self._date_key(row.get("order_date") or row.get("created_at"))
            if not day:
                continue
            grouped[day]["pedidos"] += 1
            grouped[day]["monto"] += self._number(row.get("total_amount"))
        return [
            {"fecha": day, "pedidos": value["pedidos"], "monto": round(value["monto"], 2)}
            for day, value in sorted(grouped.items())[-14:]
        ]

    def _estado_pedidos(self, orders):
        counts = Counter((row.get("status") or "sin_estado") for row in orders)
        return [{"estado": key, "cantidad": value} for key, value in counts.most_common()]

    def _mensajes_por_dia(self, messages):
        grouped = defaultdict(lambda: {"usuario": 0, "bot": 0})
        for row in messages:
            day = self._date_key(row.get("created_at"))
            if not day:
                continue
            sender = str(row.get("sender_type") or "").lower()
            if sender in ("bot", "assistant"):
                grouped[day]["bot"] += 1
            else:
                grouped[day]["usuario"] += 1
        return [
            {"fecha": day, "usuario": value["usuario"], "bot": value["bot"]}
            for day, value in sorted(grouped.items())[-14:]
        ]

    def _intents_frecuentes(self, messages):
        user_messages = [
            row for row in messages
            if str(row.get("sender_type") or "").lower() in ("user", "usuario")
        ]
        counts = Counter((row.get("intent") or "consulta_general") for row in user_messages)
        total = sum(counts.values()) or 1
        return [
            {
                "intent": key,
                "cantidad": value,
                "porcentaje": round((value / total) * 100),
            }
            for key, value in counts.most_common(8)
        ]

    def _actividad_por_hora(self, messages):
        counts = Counter()
        for row in messages:
            parsed = self._parse_datetime(row.get("created_at"))
            if parsed:
                counts[parsed.hour] += 1
        return [{"hora": hour, "mensajes": counts.get(hour, 0)} for hour in range(24)]

    def _productos_mas_consultados(self, interactions, product_by_id, promo_by_id):
        counts = Counter()
        for row in interactions:
            item_id = row.get("product_id") or row.get("promotion_id")
            if item_id:
                counts[item_id] += 1
        result = []
        for item_id, count in counts.most_common(8):
            detail = product_by_id.get(item_id) or promo_by_id.get(item_id) or {}
            result.append({
                "nombre": detail.get("name") or detail.get("title") or detail.get("nombre") or item_id,
                "consultas": count,
            })
        return result

    def _segmentos_usuarios(self, users):
        counts = Counter((row.get("segment") or "sin_segmento") for row in users)
        return [{"segmento": key, "cantidad": value} for key, value in counts.most_common()]

    def _top_clientes(self, orders, user_by_id):
        grouped = defaultdict(float)
        for row in orders:
            user_id = row.get("user_id")
            if user_id:
                grouped[user_id] += self._number(row.get("total_amount"))
        result = []
        for user_id, total in sorted(grouped.items(), key=lambda item: item[1], reverse=True)[:8]:
            user = user_by_id.get(user_id) or {}
            result.append({
                "nombre": user.get("name_alias") or user.get("user_code") or user_id,
                "segmento": user.get("segment") or "sin_segmento",
                "monto_total": round(total, 2),
            })
        return result

    def _funnel_conversion(self, conversations, recommendations, orders, feedback):
        return [
            {"etapa": "Conversaciones", "cantidad": len(conversations)},
            {"etapa": "Recomendaciones", "cantidad": len(recommendations)},
            {"etapa": "Pedidos", "cantidad": len(orders)},
            {"etapa": "Feedback", "cantidad": len(feedback)},
        ]

    def _efectividad_recomendaciones(self, recommendations):
        total = len(recommendations)
        accepted = sum(1 for row in recommendations if row.get("was_selected") is True)
        scores = [self._number(row.get("score")) for row in recommendations if row.get("score") is not None]
        return {
            "total_recomendaciones": total,
            "aceptadas": accepted,
            "tasa_aceptacion": round((accepted / total) * 100, 1) if total else 0,
            "score_promedio": round(sum(scores) / len(scores), 2) if scores else 0,
        }

    def _feedback(self, feedback):
        ratings = [int(self._number(row.get("rating"), 0)) for row in feedback if row.get("rating") is not None]
        counts = Counter(ratings)
        return {
            "promedio": round(sum(ratings) / len(ratings), 2) if ratings else 0,
            "total_respuestas": len(ratings),
            "distribucion": [
                {"estrellas": stars, "cantidad": counts.get(stars, 0)}
                for stars in range(1, 6)
            ],
        }

    def _date_key(self, value):
        parsed = self._parse_datetime(value)
        return parsed.date().isoformat() if parsed else None

    def _parse_datetime(self, value):
        if not value:
            return None
        text = str(value).replace("Z", "+00:00")
        try:
            return datetime.fromisoformat(text)
        except Exception:
            try:
                return datetime.strptime(text[:10], "%Y-%m-%d")
            except Exception:
                return None

    def _number(self, value, default=0):
        try:
            return float(value)
        except Exception:
            return float(default)
