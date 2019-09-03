from rest_framework import serializers
from .models import *

class TestSerializer(serializers.ModelSerializer):
	class Meta:
		model = ClientModel
		fields = '__all__'
