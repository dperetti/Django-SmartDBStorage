from django.core.files.base import ContentFile
from django.test import TestCase
from .storage import SmartDBStorage


class SmartDBStorageTest(TestCase):

    def setUp(self):
        self.storage = SmartDBStorage()

    def test_file_creation_and_deletion(self):
        """
        Super basic test.
        """
        full_name = 'pool/some_file'

        # save something and get the name it was assigned to
        created_file_name = self.storage.save(full_name, ContentFile(b"these are bytes"))

        # Did we create "some_file" in the "pool" ?
        self.assertTrue(self.storage.exists(created_file_name))

        # Is it the same content ?
        f = self.storage.open(created_file_name)
        self.assertEqual(f.read(), ContentFile(b"these are bytes").read())

        # Delete it and check it still exists
        self.storage.delete(created_file_name)
        self.assertFalse(self.storage.exists(created_file_name))
