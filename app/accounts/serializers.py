from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

#This handles most of the user registration/login
class RegisterSerializer(serializers.ModelSerializer):
    #minimum password length and pass is write only for security
    password = serializers.CharField(write_only=True, min_length=8)
    pswrdAgain = serializers.CharField(write_only=True, min_length=8)
    class Meta:
        model = User
        fields = ("username", "email", "password", "pswrdAgain", "role")

#make sure passwords match, validate the two passwords!
    def validate(self, attrs):
        if attrs["password"] != attrs["pswrdAgain"]:
            raise serializers.ValidationError({"Passwords do not match."})
        return attrs
#checks value, blocks any self made admins
    def validate_role(self, value):
        if value == "admin":
            raise serializers.ValidationError("Admin accounts cannot be self-registered.")
        return value
#creates a new user object
    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        #set_password will hash the password (was in SRS...im pretty sure)
        user.set_password(password) 
        user.save()
        return user

#this can be used for a access token!
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email", "role")