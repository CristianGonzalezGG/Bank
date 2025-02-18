def notifications_processor(request):
    if request.user.is_authenticated:
        try:
            unread_notifications_count = Notification.objects.filter(
                client=request.user.client,
                read=False
            ).count()
            recent_notifications = Notification.objects.filter(
                client=request.user.client
            ).order_by('-created_at')[:5]
        except (AttributeError, Client.DoesNotExist):
            unread_notifications_count = 0
            recent_notifications = []
    else:
        unread_notifications_count = 0
        recent_notifications = []

    return {
        'unread_notifications_count': unread_notifications_count,
        'recent_notifications': recent_notifications,
    } 