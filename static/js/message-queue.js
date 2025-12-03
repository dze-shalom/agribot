/**
 * Message Queue Manager for AgriBot
 * Handles offline message queuing and synchronization
 */

class MessageQueue {
    constructor(storage) {
        this.storage = storage;
        this.syncInProgress = false;
        this.syncInterval = null;
        this.maxRetries = 3;
        this.retryDelay = 2000; // 2 seconds
        this.listeners = {
            'queue-updated': [],
            'sync-started': [],
            'sync-completed': [],
            'sync-failed': [],
            'message-sent': [],
            'message-failed': []
        };
    }

    /**
     * Add event listener
     */
    on(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event].push(callback);
        }
    }

    /**
     * Emit event to listeners
     */
    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }

    /**
     * Queue a message for later sending
     */
    async queueMessage(message) {
        try {
            const id = await this.storage.queueMessage(message);
            console.log('[MessageQueue] Message queued:', id);

            this.emit('queue-updated', {
                action: 'added',
                messageId: id,
                queueSize: await this.getQueueSize()
            });

            // Try to sync immediately if online
            if (navigator.onLine) {
                this.syncMessages();
            }

            return id;
        } catch (error) {
            console.error('[MessageQueue] Failed to queue message:', error);
            throw error;
        }
    }

    /**
     * Get queue size
     */
    async getQueueSize() {
        const messages = await this.storage.getQueuedMessages();
        return messages.filter(m => m.status === 'pending').length;
    }

    /**
     * Get all queued messages
     */
    async getQueuedMessages() {
        return await this.storage.getQueuedMessages();
    }

    /**
     * Sync queued messages with server
     */
    async syncMessages() {
        // Prevent concurrent syncs
        if (this.syncInProgress) {
            console.log('[MessageQueue] Sync already in progress');
            return;
        }

        // Check if online
        if (!navigator.onLine) {
            console.log('[MessageQueue] Cannot sync - offline');
            return;
        }

        this.syncInProgress = true;
        this.emit('sync-started', {});

        try {
            const messages = await this.storage.getQueuedMessages();
            const pendingMessages = messages.filter(m => m.status === 'pending');

            console.log(`[MessageQueue] Syncing ${pendingMessages.length} messages`);

            let successCount = 0;
            let failCount = 0;

            for (const message of pendingMessages) {
                try {
                    const success = await this.sendMessage(message);

                    if (success) {
                        await this.storage.removeQueuedMessage(message.id);
                        successCount++;

                        this.emit('message-sent', {
                            messageId: message.id,
                            message: message
                        });
                    } else {
                        // Increment retry count
                        const retryCount = (message.retryCount || 0) + 1;

                        if (retryCount >= this.maxRetries) {
                            // Mark as failed after max retries
                            await this.storage.updateQueuedMessage(message.id, {
                                status: 'failed',
                                retryCount: retryCount,
                                lastError: 'Max retries exceeded'
                            });
                            failCount++;

                            this.emit('message-failed', {
                                messageId: message.id,
                                message: message,
                                reason: 'Max retries exceeded'
                            });
                        } else {
                            // Update retry count
                            await this.storage.updateQueuedMessage(message.id, {
                                retryCount: retryCount
                            });
                        }
                    }
                } catch (error) {
                    console.error('[MessageQueue] Failed to send message:', error);

                    // Increment retry count
                    const retryCount = (message.retryCount || 0) + 1;

                    if (retryCount >= this.maxRetries) {
                        await this.storage.updateQueuedMessage(message.id, {
                            status: 'failed',
                            retryCount: retryCount,
                            lastError: error.message
                        });
                        failCount++;

                        this.emit('message-failed', {
                            messageId: message.id,
                            message: message,
                            reason: error.message
                        });
                    } else {
                        await this.storage.updateQueuedMessage(message.id, {
                            retryCount: retryCount,
                            lastError: error.message
                        });
                    }
                }

                // Small delay between messages
                await this.delay(100);
            }

            console.log(`[MessageQueue] Sync complete - ${successCount} sent, ${failCount} failed`);

            this.emit('sync-completed', {
                successCount: successCount,
                failCount: failCount,
                remainingCount: await this.getQueueSize()
            });

        } catch (error) {
            console.error('[MessageQueue] Sync failed:', error);
            this.emit('sync-failed', { error: error.message });
        } finally {
            this.syncInProgress = false;

            this.emit('queue-updated', {
                action: 'synced',
                queueSize: await this.getQueueSize()
            });
        }
    }

    /**
     * Send a single message to the server
     */
    async sendMessage(message) {
        try {
            const formData = new FormData();
            formData.append('message', message.content);

            if (message.image) {
                // Handle image data if present
                if (message.image.blob) {
                    formData.append('image', message.image.blob, message.image.filename);
                }
            }

            const response = await fetch('/api/chatbot/message', {
                method: 'POST',
                body: formData,
                headers: {
                    // Don't set Content-Type - browser will set it with boundary for FormData
                }
            });

            if (response.ok) {
                const data = await response.json();
                console.log('[MessageQueue] Message sent successfully:', data);
                return true;
            } else {
                console.error('[MessageQueue] Server returned error:', response.status);
                return false;
            }
        } catch (error) {
            console.error('[MessageQueue] Network error:', error);
            throw error;
        }
    }

    /**
     * Retry failed messages
     */
    async retryFailedMessages() {
        try {
            const messages = await this.storage.getQueuedMessages();
            const failedMessages = messages.filter(m => m.status === 'failed');

            for (const message of failedMessages) {
                // Reset status to pending and clear retry count
                await this.storage.updateQueuedMessage(message.id, {
                    status: 'pending',
                    retryCount: 0,
                    lastError: null
                });
            }

            console.log(`[MessageQueue] ${failedMessages.length} failed messages reset for retry`);

            // Trigger sync
            if (navigator.onLine) {
                this.syncMessages();
            }
        } catch (error) {
            console.error('[MessageQueue] Failed to retry messages:', error);
        }
    }

    /**
     * Clear all queued messages
     */
    async clearQueue() {
        try {
            await this.storage.clearMessageQueue();
            console.log('[MessageQueue] Queue cleared');

            this.emit('queue-updated', {
                action: 'cleared',
                queueSize: 0
            });
        } catch (error) {
            console.error('[MessageQueue] Failed to clear queue:', error);
            throw error;
        }
    }

    /**
     * Start automatic sync on connection restore
     */
    startAutoSync() {
        // Sync when coming online
        window.addEventListener('online', () => {
            console.log('[MessageQueue] Connection restored - syncing');
            this.syncMessages();
        });

        // Periodic sync check
        this.syncInterval = setInterval(() => {
            if (navigator.onLine && !this.syncInProgress) {
                this.getQueueSize().then(size => {
                    if (size > 0) {
                        console.log('[MessageQueue] Periodic sync check - messages pending');
                        this.syncMessages();
                    }
                });
            }
        }, 60000); // Check every minute

        console.log('[MessageQueue] Auto-sync started');
    }

    /**
     * Stop automatic sync
     */
    stopAutoSync() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
            this.syncInterval = null;
            console.log('[MessageQueue] Auto-sync stopped');
        }
    }

    /**
     * Get queue statistics
     */
    async getStats() {
        const messages = await this.storage.getQueuedMessages();

        return {
            total: messages.length,
            pending: messages.filter(m => m.status === 'pending').length,
            failed: messages.filter(m => m.status === 'failed').length,
            oldest: messages.length > 0 ? Math.min(...messages.map(m => m.timestamp)) : null,
            newest: messages.length > 0 ? Math.max(...messages.map(m => m.timestamp)) : null
        };
    }

    /**
     * Delay helper
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}

// Export for use in chatbot
if (typeof window !== 'undefined') {
    window.MessageQueue = MessageQueue;
}
