from User.models import User
from rest_framework import serializers
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'password', 'email', 'phone_number', 'role', 'profile_picture', 'bio', 'is_verified', 'is_active', 'is_staff', 'date_joined', 'last_login']
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def validate_role(self, value):
        role_field = User._meta.get_field('role') if hasattr(User, '_meta') else None
        if hasattr(User, 'ROLE_CHOICES'):
            role_choices = [choice[0] for choice in getattr(User, 'ROLE_CHOICES', [])]
        elif role_field and hasattr(role_field, 'choices'):
            role_choices = [choice[0] for choice in role_field.choices]
        else:
            role_choices = []
        if value not in role_choices:
            raise serializers.ValidationError("Invalid role specified.")
        return value