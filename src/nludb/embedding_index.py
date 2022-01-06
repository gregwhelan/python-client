import logging
import json
from typing import Union, List, Dict

from nludb import __version__
from nludb.api.base import ApiBase, AsyncTask, NludbResponse
from nludb.types.base import Metadata
from nludb.types.embedding_index import *

__author__ = "Edward Benson"
__copyright__ = "Edward Benson"
__license__ = "MIT"

_logger = logging.getLogger(__name__)

class EmbeddingIndex:
  """A persistent, read-optimized index over embeddings.
  """

  def __init__(self, nludb: ApiBase, id: str, name: str):
    self.nludb = nludb
    self.name = name
    self.id = id

  def insert_file(
    self, 
    fileId: str,
    blockType: str = None,
    externalId: str = None,
    externalType: str = None,
    metadata: Union[int, float, bool, str, List, Dict] = None,
    reindex: bool = True,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> NludbResponse[IndexInsertResponse]:    
    if isinstance(metadata, dict) or isinstance(metadata, list):
      metadata = json.dumps(metadata)

    req = IndexInsertRequest(
      self.id,
      fileId=fileId,
      blockType=blockType,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata,
      reindex=reindex,
    )
    return self.nludb.post(
      'embedding-index/insert',
      req,
      expect=IndexInsertResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def insert_many(
    self,
    items: List[Union[IndexItem, str]],
    reindex: bool=True,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> NludbResponse[IndexInsertResponse]:
    newItems = []
    for item in items:
      if type(item) == str:
        newItems.append(IndexItem(value=item))
      else:
        newItems.append(item)

    req = IndexInsertRequest(
      indexId=self.id,
      value=None,
      items=[item.clone_for_insert() for item in newItems],
      reindex=reindex,
    )
    return self.nludb.post(
      'embedding-index/insert',
      req,
      expect=IndexInsertResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def insert(
    self, 
    value: str,
    externalId: str = None,
    externalType: str = None,
    metadata: Union[int, float, bool, str, List, Dict] = None,
    reindex: bool = True,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> NludbResponse[IndexInsertResponse]:
    
    req = IndexInsertRequest(
      indexId=self.id,
      value=value,
      items=None,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata_to_str(metadata),
      reindex=reindex,
    )
    return self.nludb.post(
      'embedding-index/insert',
      req,
      expect=IndexInsertResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def embed(
    self,
    spaceId: str = None,
    spaceHandle: str = None) -> NludbResponse[IndexEmbedResponse]:
    req = IndexEmbedRequest(
      self.id
    )
    return self.nludb.post(
      'embedding-index/embed',
      req,
      expect=IndexEmbedRequest,
      asynchronous=True,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def create_snapshot(
    self,
    spaceId: str = None,
    spaceHandle: str = None) -> NludbResponse[IndexSnapshotResponse]:
    req = IndexSnapshotRequest(
      self.id
    )
    return self.nludb.post(
      'embedding-index/snapshot/create',
      req,
      expect=IndexSnapshotRequest,
      asynchronous=True,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def list_snapshots(
    self,
    spaceId: str = None,
    spaceHandle: str = None) -> NludbResponse[ListSnapshotsResponse]:
    req = ListSnapshotsRequest(
      indexId = self.id
    )
    return self.nludb.post(
      'embedding-index/snapshot/list',
      req,
      expect=ListSnapshotsResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def list_items(
    self, 
    fileId: str = None, 
    blockId: str = None, 
    spanId: str = None,
    spaceId: str = None,
    spaceHandle: str = None) -> NludbResponse[ListItemsResponse]:
    req = ListItemsRequest(
      indexId = self.id,
      fileId = fileId,
      blockId = blockId,
      spanId = spanId
    )
    return self.nludb.post(
      'embedding-index/listItems',
      req,
      expect=ListItemsResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def delete_snapshot(
    self, 
    snapshot_id: str,
    spaceId: str = None,
    spaceHandle: str = None) -> NludbResponse[DeleteSnapshotsResponse]:
    req = DeleteSnapshotsRequest(
      snapshotId = snapshot_id
    )
    return self.nludb.post(
      'embedding-index/snapshot/delete',
      req,
      expect=DeleteSnapshotsResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def delete(
    self,
    spaceId: str = None,
    spaceHandle: str = None) -> NludbResponse[IndexDeleteResponse]:
    req = IndexDeleteRequest(
      self.id
    )
    return self.nludb.post(
      'embedding-index/delete',
      req,
      expect=IndexDeleteResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )

  def search(
    self, 
    query: Union[str, List[str]],
    k: int = 1,
    includeMetadata: bool = False,
    pd = False,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> NludbResponse[IndexSearchResponse]:
    if type(query) == list:
      req = IndexSearchRequest(
        self.id,
        query=None,
        queries=query,
        k=k,
        includeMetadata=includeMetadata,
      )
    else:
      req = IndexSearchRequest(
        self.id,
        query=query,
        queries=None,
        k=k,
        includeMetadata=includeMetadata,
      )
    ret = self.nludb.post(
      'embedding-index/search',
      req,
      expect=IndexSearchResponse,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )
    
    if pd is False:
      return ret

    import pandas as pd    
    return pd.DataFrame([(hit.score, hit.value) for hit in ret.data.hits], columns =['Score', 'Value'])

  @staticmethod
  def create(
    nludb: ApiBase,
    name: str,
    model: str,
    upsert: bool = True,
    externalId: str = None,
    externalType: str = None,
    metadata: any = None,
    spaceId: str = None,
    spaceHandle: str = None
  ) -> "EmbeddingIndex":
    req = IndexCreateRequest(
      name=name,
      model=model,
      upsert=upsert,
      externalId=externalId,
      externalType=externalType,
      metadata=metadata,
    )
    res = nludb.post(
      'embedding-index/create', 
      req,
      spaceId=spaceId,
      spaceHandle=spaceHandle
    )
    return EmbeddingIndex(
      nludb=nludb,
      name=req.name,
      id=res.data.get("id", None)
    )