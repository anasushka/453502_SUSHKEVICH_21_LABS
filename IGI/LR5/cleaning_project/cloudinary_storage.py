import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from django.core.files.storage import Storage


class CloudinaryStorage(Storage):
    def _save(self, name, content):
        public_id = os.path.splitext(name)[0]
        result = cloudinary.uploader.upload(
            content.read(),
            public_id=public_id,
            overwrite=True,
            resource_type='image',
        )
        fmt = result.get('format', 'jpg')
        return f"{result['public_id']}.{fmt}"

    def url(self, name):
        if not name:
            return ''
        if name.startswith('http'):
            return name
        public_id = os.path.splitext(name)[0]
        return cloudinary.CloudinaryImage(public_id).build_url()

    def exists(self, name):
        return False

    def delete(self, name):
        try:
            cloudinary.uploader.destroy(os.path.splitext(name)[0])
        except Exception:
            pass

    def size(self, name):
        try:
            result = cloudinary.api.resource(os.path.splitext(name)[0])
            return result.get('bytes', 0)
        except Exception:
            return 0
