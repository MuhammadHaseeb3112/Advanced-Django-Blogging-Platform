def unread_notifications(request):

    if request.user.is_authenticated:

        unread_count = request.user.notifications.filter(

            is_read=False

        ).count()

        return {

            'global_unread_notifications': unread_count

        }

    return {

        'global_unread_notifications': 0

    }