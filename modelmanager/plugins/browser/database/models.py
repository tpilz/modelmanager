"""
This is a collection of meta models to be subclassed in the projects
browser/models.py file.
"""
import os
import os.path as osp
from io import BytesIO

from django.db import models
from django.core.files.uploadedfile import InMemoryUploadedFile


class Run(models.Model):
    class Meta:
        abstract = True
    time = models.DateTimeField('Time', auto_now_add=True)
    tags = models.CharField(max_length=1024, blank=True, null=True)
    notes = models.TextField('Notes', blank=True)

    def __unicode__(self):
        return u'Run %i' % self.pk


class RunTagged(models.Model):
    class Meta:
        abstract = True
    run = models.ForeignKey('browser.Run', on_delete=models.CASCADE,
                            related_name='%(class)ss')
    tags = models.CharField(max_length=1024, blank=True, null=True)


class TaggedValue(RunTagged):
    class Meta:
        abstract = True
    MAX_DIGITS = 16
    DECIMAL_PLACES = 8
    name = models.CharField(max_length=128)
    value = models.DecimalField(max_digits=MAX_DIGITS,
                                decimal_places=DECIMAL_PLACES)


def upload_to_path(instance, filename):
    return osp.join(instance.dirname, str(instance.run.pk), filename)


class File(models.Model):
    """
    An abstract model to save files with a run instance. Unlike the Django file
    field defaults, it accepts any file or buffer instance and file path to the
    file argument. Moving/copying happens in memory, so this is not suitable
    for large files.

    Additional arguments:
    ---------------------
    filename: destination file name. Required if a buffer is parsed to file.
    copy: boolean whether to copy the source file or to move it.

    Class options:
    --------------
    copy: default to the copy argument.
    dirname: name of directory under the browser/files directory the files are
        saved under before the runID.
    """
    class Meta:
        abstract = True
    # name of subdirectory the files are stored under: dirname/runid/files
    dirname = 'runs'
    # whether to copy or move the original file
    copy = True
    # file Django fields
    file = models.FileField(upload_to=upload_to_path)

    def __init__(self, *args, **kwargs):
        f = kwargs.pop('file', None)
        if f is not None:
            self.parsed_file = f
            self.parsed_filename = kwargs.pop('filename', None)
            self.copy = kwargs.pop('copy', self.copy)
            kwargs['file'] = self._handle_file()
        super(File, self).__init__(*args, **kwargs)

    def _handle_file(self):
        """
        Converts a filepath, file object or buffer to a InMemoryUploadedFile.
        """
        fla = ('read', 'seek', 'close', 'name')
        if all([hasattr(self.parsed_file, a) for a in fla]):
            self.parsed_file.close()
            self.parsed_file = self.parsed_file.name
        # read persistent files into a a BytesIO buffer
        if type(self.parsed_file) == str:
            with open(self.parsed_file, 'rb') as bf:
                buf = BytesIO(bf.read())
            fn = osp.basename(self.parsed_file)
            if not self.copy:
                os.remove(self.parsed_file.name)
        else:
            buf = self.parsed_file
            fn = self.parsed_filename
        imf = InMemoryUploadedFile(buf, None, fn, None, None, None)
        try:
            imf.readable()
        except Exception:
            raise IOError('File not readable: %s' % self.parsed_file)
        return imf

    def delete(self):
        self.file.delete()
        super(File, self).delete()
