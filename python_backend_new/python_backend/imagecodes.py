import base64

# Create your views here.
from rest_framework.response import Response
from rest_framework.views import APIView

from django_redis import get_redis_connection
from public_tools.captcha.captcha import captcha

import uuid

# 前端访问地址 120.77.58.203:8765/imagecodes

class ImageCodeView(APIView):
    permission_classes = ()
    authentication_classes = ()

    def get(self,request):

        #image_code_id = gen_uuid32()
        image_code_id = str(uuid.uuid1())
        text,image = captcha.generate_captcha()
        image_str = base64.b64encode(image)
        s = image_str.decode()
        ss = 'data:image/jpeg;base64,%s' % s
        redis_conn = get_redis_connection('default')
        redis_conn.setex(image_code_id,300,text)

        return Response({'image_code_id':image_code_id,'image_str':ss})
        #return Response({'nihao':'nihao'})

get_image_code = ImageCodeView.as_view()