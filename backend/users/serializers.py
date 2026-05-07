from rest_framework import serializers
from .models import CustomUser
from django.contrib.auth.password_validation import validate_password

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password]
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2', 'role', 'phone', 'department']
        extra_kwargs = {
            'email': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'phone', 'department', 'first_name', 'last_name', 'last_login']


class UserAdminSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'password',
            'role',
            'phone',
            'department',
            'first_name',
            'last_name',
            'is_active',
            'last_login',
        ]
        read_only_fields = ['last_login']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance