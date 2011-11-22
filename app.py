"""
Small web service for static gallery generation.

"""

import flask
from flask import Flask
from flask import render_template

from PIL import Image

import os

app = Flask(__name__)

here_folder = os.getcwd()

static_name = 'static'
gallery_name = 'gallery'
thumbs_name = 'thumbs'
readme_name = 'README'
index_gallery_name = 'index.html'
secret_prefix_name = 'secret_'

index_title = 'Title of the gallery'
index_image_name = 'logo.jpg'

# url parse is ugly
static_url = '/%s/'
gallery_base_url = '/%s/%s/%s/'
thumbs_base_url = '/%s/%s/%s/%s/'

static_base_path = '%s/%s/'
gallery_base_path = '%s/%s/%s/'
thumbs_base_path = '%s/%s/%s/%s/'

thumbs_size = (180, 120)
image_format = "JPEG"

class Item(object):
	def __init__(self, title, url):
		self.title = title
		self.url = url

def get_gallery_urls(folder):
	"""
	Get gallery and thumbs url

	"""

	gallery_url = gallery_base_url % (static_name, gallery_name, folder)
	thumbs_url = thumbs_base_url % (static_name, gallery_name, folder, thumbs_name)

	return gallery_url, thumbs_url

def get_gallery_path(folder):
	"""
	Get gallery and thumbs path

	"""

	gallery_path = os.path.join(here_folder, gallery_base_path % (static_name, gallery_name, folder))
	thumbs_path = os.path.join(here_folder, thumbs_base_path % (static_name, gallery_name, folder, thumbs_name))

	return gallery_path, thumbs_path

@app.route('/')
def do_menu():
	"""
	Generate dynamic menu

	"""

	index_image_url = (gallery_base_url % (static_name, gallery_name, index_image_name))[:-1]

	static_path =os.path.normcase(os.path.join(here_folder, static_base_path % (static_name, gallery_name)))

	galleries = os.listdir(static_path)


	items = []

	for gallery in galleries:
		# check each gallery
		if gallery.startswith(secret_prefix_name) == False and gallery != index_image_name:
			# do not display secret one
			gallery_url, thumbs_url = get_gallery_urls(gallery)
			items.append(Item(gallery, gallery_url))

	return render_template('menu.jinja2', title=index_title, items=items, image_url=index_image_url)

@app.route('/do/gallery/<folder>/')
def do_gallery(folder):
	"""
	Compute a gallery creating static file from a template

	"""

	# process all pictures
	gallery_path, thumbs_path = get_gallery_path(folder)
	image_list = os.listdir(gallery_path)

	if thumbs_name in image_list:
		# suppress thumbnail folder
		image_list.remove(thumbs_name)

	if readme_name in image_list:
		# apply readme
		image_list.remove(readme_name)

		readme = open(gallery_path + readme_name, 'r').read()
	else:
		readme = 'No comment available !'

	if index_gallery_name in image_list:
		# simply remove
		image_list.remove(index_gallery_name)

	if os.path.exists(thumbs_path) == False:
		# create thumbs directory
		os.mkdir(thumbs_path)

	image_list.sort()

	for image in image_list:
		# create thumbs
		image_path = os.path.join(gallery_path, image)
		image_thumb_path = os.path.join(thumbs_path, image)

		image_full = Image.open(os.path.normcase(image_path))
		image_full.thumbnail(thumbs_size, Image.ANTIALIAS)
   		image_full.save(image_thumb_path, image_full.format)

	# generate template
	gallery_url, thumbs_url = get_gallery_urls(folder)
	template = render_template('base.jinja2', title=folder, thumbs_url=thumbs_url, gallery_url=gallery_url, image_list=image_list, readme=readme)

	# save static file
	new_file = file(os.path.join(gallery_path, index_gallery_name), 'w')
	new_file.write(template)
	new_file.close()

	return flask.redirect(gallery_url + index_gallery_name, code=302)

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=5000)
		