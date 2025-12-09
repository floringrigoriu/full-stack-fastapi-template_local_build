# prompt 1 : Cache Creation :

Add an interface and an implementation in python for a 3 layer cache :

- first layer in memory
- second layer on disk
- last layer : back-up on azure blob storage
The blob storage and file io store need to have an Interface that would allow testing without FILE or blob storage, and add the implementation for the blob and file storege.

The implementation for loading from file and blob store needs to have async load

# Prompt 2 : Move Cache memory / local disk to LRU

Update the Cache implementation to add a eviction policy : both memory and local file cache have a maximum capacity configurable. on exhausting of capacity, the least recent items are to be evicted.
The capacity is expressed either in number of item , or by total size of the value stored in the cache


# prompt 3 : Refactor, reuse LRU mechanism

Extract the RLU implementation for the memory getter and the file getter, such there is a single RLU code that is reused across both implementation, with injection to the removal callback :
- for memory is removing from memory
- for disk is deleting the file
The LRU utility class should be in a separate file and should be passed as constructor parameter for each of the 2 implementation 
further more disk cache has an order of magnitude bigger storage space than memory

# prompt 4 : Mage Cache Generic

Refactor existing implementation of ThreeLayerCache, making generic where there are n layers of caching each subsequent layer is cheaper but also slower.

Last layer, it is a fallback with guarantee of that data being present in it.

On retrieval of data from a cheaper layer the more expensive layers will be copied that data also

this generic n-layer cache will be having an class extending named EfficientVectorStorage, whith the 3 layers currently implemented by cache : Memory, disk and blob storage


# prompt 5 : remove reflection calls and move to interface

For the cache implementation of NLayerCache make sure the the constructor takes layers  implementing a common interface , Make each of the memory, file and blob storage implement that interface, such no need to call reflection to verify if methods are defined


# prompt 6 : implement a vector search

Define a vector search interface, and an implementation in VectorSearch.Py,  which for a a given vector of floats return topK closest vectors, the vectors are stored in memory.
- topK parameter is configurable
- topK closes vectors is based on Euclidian distance

# prompt 7 : define Vector Search for chunk index :
We maintain a list of VectorSearch instances N . The N instance is obtain by clustering the space of the vectors to N - centroids - vectors that current nodes in current chunk are the closest.

The chunks are stored in blob storage and cached in memory or on disk using the EfficientVectorStorage utility class

for a given target vector, get the centroid closes to the target vector using an instance of the VectorSearch class.



# prompt 8 : define Routing layer

Define a Router Interface and Router implementation in router.py .  The router will manage access requests to a collection of virtual nodes in a consistent hash ring.
The virtual nodes count is set to 10000  and those will match to real nodes of 10

algorithm :
- the centroids for vector search chunks will be place on the hash ring based on the hash of the centroid 
- To locate the centroid, we will locate a vector search from current target vector to the list of centroids

- from the centroid we determine we determine the virtual node and read node should hold that  centroid

- we issue the request to get topK closest vectors on the cache in the corresponding real node 

- The caching layer should soupport followying API:
  - GetSearch(targetVector)
  - GetNumberOfRealNodes()
  - IncreaseRealNodesCount()
  - DecreaseRealNodesCount() 

# prompt 9 : fix the consistent hashing - it looks on resizing all virtual nodes are moved, which is not the objective of the algorithm

