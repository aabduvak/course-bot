from rest_framework.serializers import ModelSerializer

from .models import User, Message, Content, Button

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class ContentSerializer(ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'

class ButtonSerializer(ModelSerializer):
    class Meta:
        model = Button
        field = '__all__'