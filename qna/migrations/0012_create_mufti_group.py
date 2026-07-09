from django.db import migrations


def create_mufti_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    User = apps.get_model('user_management', 'User')

    # Create Mufti group
    mufti_group, created = Group.objects.get_or_create(name='Mufti')

    # Assign all users with role='mufti' to the Mufti group
    mufti_users = User.objects.filter(role='mufti')
    for user in mufti_users:
        user.groups.add(mufti_group)

    # Also give Mufti group staff status so they can access admin
    for user in mufti_users:
        if not user.is_staff:
            user.is_staff = True
            user.save()


def reverse_mufti_group(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    User = apps.get_model('user_management', 'User')

    try:
        mufti_group = Group.objects.get(name='Mufti')
        mufti_users = User.objects.filter(role='mufti')
        for user in mufti_users:
            user.groups.remove(mufti_group)
        mufti_group.delete()
    except Group.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('qna', '0011_answer_updated_by_manual_answer_updated_by_user_and_more'),
        ('user_management', '0003_user_current_hadith_book_user_current_hadith_number_and_more'),
    ]

    operations = [
        migrations.RunPython(create_mufti_group, reverse_mufti_group),
    ]
