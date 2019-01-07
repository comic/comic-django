from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.views import View
from PIL import Image as PILImage
from rest_framework import status
from django.http.response import HttpResponse
import numpy as np
import SimpleITK as sitk
from grandchallenge.retina_api.mixins import RetinaAPIPermissionMixin
from grandchallenge.cases.models import Image


class IndexView(RetinaAPIPermissionMixin, View):
    def get(self, request):
        return render(request, "pages/home.html")


class ThumbnailView(RetinaAPIPermissionMixin, View):
    """
    View class for returning a thumbnail of an image as png (max height/width: 128px)
    """

    raise_exception = True  # Raise 403 on unauthenticated request

    def get(self, request, image_id):
        image_object = get_object_or_404(Image, pk=image_id)
        image_itk = image_object.get_sitk_image()
        if image_itk is None:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        depth = image_itk.GetDepth()
        image_nparray = sitk.GetArrayFromImage(image_itk)
        if depth > 0:
            # Get middle slice of image if 3D
            image_nparray = image_nparray[depth // 2]
        image = PILImage.fromarray(image_nparray)
        image.thumbnail((128, 128), PILImage.ANTIALIAS)
        response = HttpResponse(content_type="image/png")
        image.save(response, "png")
        return response


class NumpyView(RetinaAPIPermissionMixin, View):
    """
    View class for returning a specific image as a numpy array
    """

    raise_exception = True  # Raise 403 on unauthenticated request

    def get(self, request, image_id):
        image_object = get_object_or_404(Image, pk=image_id)

        image_itk = image_object.get_sitk_image()
        if image_itk is None:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)
        npy = sitk.GetArrayFromImage(image_itk)

        # return numpy array as response
        response = HttpResponse(content_type="application/octet-stream")
        np.save(response, npy)
        return response
