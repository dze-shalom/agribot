/**
 * IndexedDB Manager for AgriBot Offline Storage
 * Handles offline data storage for conversations, knowledge base, and message queue
 */

class OfflineStorage {
    constructor() {
        this.dbName = 'AgribotDB';
        this.dbVersion = 1;
        this.db = null;
    }

    /**
     * Initialize IndexedDB
     */
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onerror = () => {
                console.error('[IndexedDB] Failed to open database:', request.error);
                reject(request.error);
            };

            request.onsuccess = () => {
                this.db = request.result;
                console.log('[IndexedDB] Database opened successfully');
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                console.log('[IndexedDB] Upgrading database...');

                // Message Queue Store
                if (!db.objectStoreNames.contains('messageQueue')) {
                    const messageStore = db.createObjectStore('messageQueue', {
                        keyPath: 'id',
                        autoIncrement: true
                    });
                    messageStore.createIndex('timestamp', 'timestamp', { unique: false });
                    messageStore.createIndex('status', 'status', { unique: false });
                }

                // Conversations Store
                if (!db.objectStoreNames.contains('conversations')) {
                    const conversationStore = db.createObjectStore('conversations', {
                        keyPath: 'id'
                    });
                    conversationStore.createIndex('timestamp', 'timestamp', { unique: false });
                    conversationStore.createIndex('sessionId', 'sessionId', { unique: true });
                }

                // Messages Store
                if (!db.objectStoreNames.contains('messages')) {
                    const messagesStore = db.createObjectStore('messages', {
                        keyPath: 'id',
                        autoIncrement: true
                    });
                    messagesStore.createIndex('conversationId', 'conversationId', { unique: false });
                    messagesStore.createIndex('timestamp', 'timestamp', { unique: false });
                }

                // Knowledge Base Store
                if (!db.objectStoreNames.contains('knowledgeBase')) {
                    const knowledgeStore = db.createObjectStore('knowledgeBase', {
                        keyPath: 'id'
                    });
                    knowledgeStore.createIndex('category', 'category', { unique: false });
                    knowledgeStore.createIndex('lastUpdated', 'lastUpdated', { unique: false });
                }

                // User Preferences Store
                if (!db.objectStoreNames.contains('preferences')) {
                    db.createObjectStore('preferences', { keyPath: 'key' });
                }

                // Cache Metadata Store
                if (!db.objectStoreNames.contains('cacheMetadata')) {
                    const cacheStore = db.createObjectStore('cacheMetadata', {
                        keyPath: 'key'
                    });
                    cacheStore.createIndex('expiresAt', 'expiresAt', { unique: false });
                }

                console.log('[IndexedDB] Database schema created');
            };
        });
    }

    /**
     * Message Queue Operations
     */
    async queueMessage(message) {
        const transaction = this.db.transaction(['messageQueue'], 'readwrite');
        const store = transaction.objectStore('messageQueue');

        const queuedMessage = {
            content: message.content,
            image: message.image || null,
            timestamp: Date.now(),
            status: 'pending',
            retryCount: 0
        };

        return new Promise((resolve, reject) => {
            const request = store.add(queuedMessage);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getQueuedMessages() {
        const transaction = this.db.transaction(['messageQueue'], 'readonly');
        const store = transaction.objectStore('messageQueue');

        return new Promise((resolve, reject) => {
            const request = store.getAll();
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async updateQueuedMessage(id, updates) {
        const transaction = this.db.transaction(['messageQueue'], 'readwrite');
        const store = transaction.objectStore('messageQueue');

        return new Promise((resolve, reject) => {
            const getRequest = store.get(id);

            getRequest.onsuccess = () => {
                const message = getRequest.result;
                if (message) {
                    Object.assign(message, updates);
                    const updateRequest = store.put(message);
                    updateRequest.onsuccess = () => resolve(updateRequest.result);
                    updateRequest.onerror = () => reject(updateRequest.error);
                } else {
                    reject(new Error('Message not found'));
                }
            };

            getRequest.onerror = () => reject(getRequest.error);
        });
    }

    async removeQueuedMessage(id) {
        const transaction = this.db.transaction(['messageQueue'], 'readwrite');
        const store = transaction.objectStore('messageQueue');

        return new Promise((resolve, reject) => {
            const request = store.delete(id);
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    async clearMessageQueue() {
        const transaction = this.db.transaction(['messageQueue'], 'readwrite');
        const store = transaction.objectStore('messageQueue');

        return new Promise((resolve, reject) => {
            const request = store.clear();
            request.onsuccess = () => resolve();
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Conversation Operations
     */
    async saveConversation(conversation) {
        const transaction = this.db.transaction(['conversations'], 'readwrite');
        const store = transaction.objectStore('conversations');

        const conversationData = {
            id: conversation.id || Date.now().toString(),
            sessionId: conversation.sessionId,
            timestamp: conversation.timestamp || Date.now(),
            lastUpdated: Date.now(),
            metadata: conversation.metadata || {}
        };

        return new Promise((resolve, reject) => {
            const request = store.put(conversationData);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getConversation(id) {
        const transaction = this.db.transaction(['conversations'], 'readonly');
        const store = transaction.objectStore('conversations');

        return new Promise((resolve, reject) => {
            const request = store.get(id);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getAllConversations() {
        const transaction = this.db.transaction(['conversations'], 'readonly');
        const store = transaction.objectStore('conversations');

        return new Promise((resolve, reject) => {
            const request = store.getAll();
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Message Operations
     */
    async saveMessage(message) {
        const transaction = this.db.transaction(['messages'], 'readwrite');
        const store = transaction.objectStore('messages');

        const messageData = {
            conversationId: message.conversationId,
            content: message.content,
            type: message.type, // 'user' or 'bot'
            timestamp: message.timestamp || Date.now(),
            image: message.image || null,
            metadata: message.metadata || {}
        };

        return new Promise((resolve, reject) => {
            const request = store.add(messageData);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getMessagesByConversation(conversationId) {
        const transaction = this.db.transaction(['messages'], 'readonly');
        const store = transaction.objectStore('messages');
        const index = store.index('conversationId');

        return new Promise((resolve, reject) => {
            const request = index.getAll(conversationId);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async deleteConversationMessages(conversationId) {
        const transaction = this.db.transaction(['messages'], 'readwrite');
        const store = transaction.objectStore('messages');
        const index = store.index('conversationId');

        return new Promise((resolve, reject) => {
            const request = index.getAllKeys(conversationId);

            request.onsuccess = () => {
                const keys = request.result;
                const deletePromises = keys.map(key => {
                    return new Promise((res, rej) => {
                        const deleteRequest = store.delete(key);
                        deleteRequest.onsuccess = () => res();
                        deleteRequest.onerror = () => rej(deleteRequest.error);
                    });
                });

                Promise.all(deletePromises)
                    .then(() => resolve())
                    .catch(reject);
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Knowledge Base Operations
     */
    async cacheKnowledge(category, data) {
        const transaction = this.db.transaction(['knowledgeBase'], 'readwrite');
        const store = transaction.objectStore('knowledgeBase');

        const knowledgeData = {
            id: category,
            category: category,
            data: data,
            lastUpdated: Date.now(),
            expiresAt: Date.now() + (7 * 24 * 60 * 60 * 1000) // 7 days
        };

        return new Promise((resolve, reject) => {
            const request = store.put(knowledgeData);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getKnowledge(category) {
        const transaction = this.db.transaction(['knowledgeBase'], 'readonly');
        const store = transaction.objectStore('knowledgeBase');

        return new Promise((resolve, reject) => {
            const request = store.get(category);

            request.onsuccess = () => {
                const result = request.result;

                // Check if data has expired
                if (result && result.expiresAt < Date.now()) {
                    resolve(null); // Return null if expired
                } else {
                    resolve(result);
                }
            };

            request.onerror = () => reject(request.error);
        });
    }

    async getAllKnowledge() {
        const transaction = this.db.transaction(['knowledgeBase'], 'readonly');
        const store = transaction.objectStore('knowledgeBase');

        return new Promise((resolve, reject) => {
            const request = store.getAll();

            request.onsuccess = () => {
                const results = request.result.filter(item => {
                    return item.expiresAt >= Date.now();
                });
                resolve(results);
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Preferences Operations
     */
    async savePreference(key, value) {
        const transaction = this.db.transaction(['preferences'], 'readwrite');
        const store = transaction.objectStore('preferences');

        const preferenceData = {
            key: key,
            value: value,
            lastUpdated: Date.now()
        };

        return new Promise((resolve, reject) => {
            const request = store.put(preferenceData);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getPreference(key) {
        const transaction = this.db.transaction(['preferences'], 'readonly');
        const store = transaction.objectStore('preferences');

        return new Promise((resolve, reject) => {
            const request = store.get(key);
            request.onsuccess = () => {
                resolve(request.result ? request.result.value : null);
            };
            request.onerror = () => reject(request.error);
        });
    }

    async getAllPreferences() {
        const transaction = this.db.transaction(['preferences'], 'readonly');
        const store = transaction.objectStore('preferences');

        return new Promise((resolve, reject) => {
            const request = store.getAll();
            request.onsuccess = () => {
                const prefs = {};
                request.result.forEach(item => {
                    prefs[item.key] = item.value;
                });
                resolve(prefs);
            };
            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Cache Metadata Operations
     */
    async setCacheMetadata(key, value, ttl = 3600000) {
        const transaction = this.db.transaction(['cacheMetadata'], 'readwrite');
        const store = transaction.objectStore('cacheMetadata');

        const cacheData = {
            key: key,
            value: value,
            createdAt: Date.now(),
            expiresAt: Date.now() + ttl
        };

        return new Promise((resolve, reject) => {
            const request = store.put(cacheData);
            request.onsuccess = () => resolve(request.result);
            request.onerror = () => reject(request.error);
        });
    }

    async getCacheMetadata(key) {
        const transaction = this.db.transaction(['cacheMetadata'], 'readonly');
        const store = transaction.objectStore('cacheMetadata');

        return new Promise((resolve, reject) => {
            const request = store.get(key);

            request.onsuccess = () => {
                const result = request.result;

                // Check if cache has expired
                if (result && result.expiresAt < Date.now()) {
                    resolve(null);
                } else {
                    resolve(result ? result.value : null);
                }
            };

            request.onerror = () => reject(request.error);
        });
    }

    /**
     * Utility Methods
     */
    async clearExpiredCache() {
        const now = Date.now();

        // Clear expired knowledge base entries
        const kbTransaction = this.db.transaction(['knowledgeBase'], 'readwrite');
        const kbStore = kbTransaction.objectStore('knowledgeBase');
        const kbIndex = kbStore.index('expiresAt');
        const kbRange = IDBKeyRange.upperBound(now);

        kbIndex.openCursor(kbRange).onsuccess = (event) => {
            const cursor = event.target.result;
            if (cursor) {
                cursor.delete();
                cursor.continue();
            }
        };

        // Clear expired cache metadata
        const cacheTransaction = this.db.transaction(['cacheMetadata'], 'readwrite');
        const cacheStore = cacheTransaction.objectStore('cacheMetadata');
        const cacheIndex = cacheStore.index('expiresAt');
        const cacheRange = IDBKeyRange.upperBound(now);

        cacheIndex.openCursor(cacheRange).onsuccess = (event) => {
            const cursor = event.target.result;
            if (cursor) {
                cursor.delete();
                cursor.continue();
            }
        };

        console.log('[IndexedDB] Expired cache cleared');
    }

    async getStorageInfo() {
        if ('storage' in navigator && 'estimate' in navigator.storage) {
            const estimate = await navigator.storage.estimate();
            return {
                usage: estimate.usage,
                quota: estimate.quota,
                percentUsed: ((estimate.usage / estimate.quota) * 100).toFixed(2)
            };
        }
        return null;
    }

    async clearAllData() {
        const stores = [
            'messageQueue',
            'conversations',
            'messages',
            'knowledgeBase',
            'preferences',
            'cacheMetadata'
        ];

        for (const storeName of stores) {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            await new Promise((resolve, reject) => {
                const request = store.clear();
                request.onsuccess = () => resolve();
                request.onerror = () => reject(request.error);
            });
        }

        console.log('[IndexedDB] All data cleared');
    }
}

// Export singleton instance
const offlineStorage = new OfflineStorage();

// Initialize on load
if (typeof window !== 'undefined') {
    window.addEventListener('load', () => {
        offlineStorage.init().catch(error => {
            console.error('[IndexedDB] Initialization failed:', error);
        });
    });
}
