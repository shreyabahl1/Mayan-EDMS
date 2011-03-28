from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from common.utils import pretty_size, pretty_size_10
from permissions.api import check_permissions

from documents.conf.settings import STORAGE_BACKEND
from models import Document, DocumentType, DocumentPage


def get_used_size(path, file_list):
    total_size = 0
    for filename in file_list:
        try:
            total_size += STORAGE_BACKEND().size(STORAGE_BACKEND.separator.join([path, filename])) 
        except OSError:
            pass
            
    return total_size

def storage_count(path=u'.'):
    directories, files = STORAGE_BACKEND().listdir(path)
    total_count = len(files)
    total_size = get_used_size(path, files)
    
    for directory in directories:
        file_count, files_size = storage_count(directory)
        total_count += file_count
        total_size += files_size

    return total_count, total_size


def get_statistics():
    total_db_documents = Document.objects.only('id',).count()

    paragraphs = [
        _(u'Document types: %d') % DocumentType.objects.count(),
        _(u'Documents in database: %d') % total_db_documents,
    ]
    
    
    try:
        total_storage_documents, storage_used_space = storage_count()
        paragraphs.append(_(u'Documents in storage: %d') % total_storage_documents)
        paragraphs.append(_(u'Space used in storage: %s (base 2), %s (base 10), %d bytes') %
            (pretty_size(storage_used_space), pretty_size_10(storage_used_space), storage_used_space))
    except NotImplementedError:
        pass

    paragraphs.append(
        _(u'Document pages in database: %d') % DocumentPage.objects.only('id',).count(),
    )
    
    return {
        'title':_(u'Document statistics'),
        'paragraphs': paragraphs
    }
