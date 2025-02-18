import requests
from django.db.models import Sum
from datetime import datetime, timedelta
from django.conf import settings

def analyze_spending_patterns(client):
    """
    Analiza los patrones de gasto de un cliente en los últimos 30 días.
    """
    from .models import Transaction  # Importación local para evitar importaciones circulares
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    transactions = Transaction.objects.filter(
        account__client=client,
        type='WITHDRAWAL',
        date__range=[start_date, end_date]
    )
    
    # Agrupar gastos por categoría
    spending_by_category = transactions.values('category').annotate(
        total=Sum('amount')
    ).order_by('-total')
    
    # Formatear resultados
    analysis = {
        'categories': {},
        'total_spent': 0,
        'biggest_expense': None,
        'transaction_count': transactions.count()
    }
    
    for item in spending_by_category:
        category = item['category']
        amount = float(item['total'])
        analysis['categories'][category] = amount
        analysis['total_spent'] += amount
        
        if not analysis['biggest_expense'] or amount > analysis['categories'][analysis['biggest_expense']]:
            analysis['biggest_expense'] = category
    
    return analysis

def get_financial_news():
    """
    Obtiene noticias financieras usando la API de NewsAPI.
    Si no hay API key configurada, retorna noticias de ejemplo.
    """
    try:
        api_key = settings.NEWS_API_KEY
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": "finanzas OR banca OR economia",
            "language": "es",
            "sortBy": "publishedAt",
            "apiKey": api_key
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('articles', [])[:5]  # Retorna las 5 noticias más recientes
            
    except (AttributeError, requests.RequestException):
        # Si hay algún error o no hay API key, retorna noticias de ejemplo
        return [
            {
                "title": "Nuevas tendencias en banca digital",
                "description": "Las instituciones financieras están adoptando nuevas tecnologías...",
                "publishedAt": datetime.now().isoformat(),
                "url": "#"
            },
            {
                "title": "Consejos para mejorar tus finanzas personales",
                "description": "Expertos comparten estrategias para una mejor gestión financiera...",
                "publishedAt": datetime.now().isoformat(),
                "url": "#"
            },
            {
                "title": "Actualización de tasas de interés",
                "description": "El banco central anuncia cambios en las tasas de interés...",
                "publishedAt": datetime.now().isoformat(),
                "url": "#"
            }
        ]

def calculate_credit_score(client):
    """
    Calcula un puntaje crediticio básico para el cliente.
    """
    from .models import Payment, Loan
    
    score = 500  # Puntaje base
    
    # Historial de pagos
    on_time_payments = Payment.objects.filter(
        loan__client=client,
        payment_date__lte=F('loan__next_payment_date')
    ).count()
    score += min(on_time_payments * 10, 200)  # Máximo 200 puntos por pagos a tiempo
    
    # Préstamos pagados
    paid_loans = Loan.objects.filter(
        client=client,
        status='PAID'
    ).count()
    score += min(paid_loans * 30, 150)  # Máximo 150 puntos por préstamos pagados
    
    # Antigüedad como cliente
    years_as_client = (datetime.now().date() - client.created_at.date()).days / 365
    score += min(int(years_as_client * 20), 150)  # Máximo 150 puntos por antigüedad
    
    return min(score, 1000)  # Máximo puntaje de 1000

def generate_account_insights(client):
    """
    Genera insights personalizados sobre la cuenta del cliente.
    """
    from .models import Transaction
    
    insights = []
    
    # Analizar gastos recurrentes
    recurring_transactions = find_recurring_transactions(client)
    if recurring_transactions:
        insights.append({
            'type': 'recurring_expenses',
            'title': 'Gastos Recurrentes Identificados',
            'data': recurring_transactions
        })
    
    # Sugerir ahorros
    savings_potential = calculate_savings_potential(client)
    if savings_potential > 0:
        insights.append({
            'type': 'savings_suggestion',
            'title': 'Potencial de Ahorro',
            'data': {
                'amount': savings_potential,
                'message': f'Podrías ahorrar aproximadamente ${savings_potential:,.2f} al mes'
            }
        })
    
    return insights 