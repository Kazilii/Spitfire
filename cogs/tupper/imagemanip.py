from PIL import Image
import requests
from io import BytesIO


class Avatar:

	def __init__(self, url=None, filepath=None):
		self.url = url
		self.filepath = filepath

	def checksize(self=None, url=None, filepath=None, pilimage=None, size: tuple=None):
		"""Compares size of the image with provided resolution. Returns True if under specified resolution"""
		if size is None:
			size = 512, 512

		if pilimage is not None:
			if pilimage.size[0] > size[0] or pilimage.size[1] > size[1]:
				return False
			else:
				return True

		if url is not None:
			avatarfile = requests.get(url)
			avatar = Image.open(BytesIO(avatarfile.content))
			if avatar.size[0] > size[0] or avatar.size[1] > size[1]:
				return False
			else:
				return True

		if filepath is not None:
			avatar = Image.open(filepath)
			if avatar.size[0] > size[0] or avatar.size[1] > size[1]:
				return False
			else:
				return True

	def resize(self=None, url=None, filepath=None, pilimage=None, size: tuple = None):
		"""Resizes an image and returns the PIL Image data."""
		if size is None:
			size = 512, 512

		if pilimage is not None:
			pilimage.thumbnail(size, Image.ANTIALIAS)
			return pilimage

		if url is not None:
			avatarfile = requests.get(url)
			avatar = Image.open(BytesIO(avatarfile.content))
			avatar.thumbnail(size, Image.ANTIALIAS)
			return avatar

		if filepath is not None:
			avatar = Image.open(filepath)
			avatar.thumbnail(size, Image.ANTIALIAS)
			return avatar
		return
