/**
 * Knowledge Base Cache Manager for AgriBot
 * Handles offline caching of agricultural knowledge
 */

class KnowledgeCache {
    constructor(storage) {
        this.storage = storage;
        this.cacheVersion = '1.0';
        this.categories = [
            'crops',
            'diseases',
            'pests',
            'best-practices',
            'seasonal-calendar',
            'soil-management',
            'irrigation',
            'fertilizers',
            'weather-tips',
            'market-info'
        ];
    }

    /**
     * Initialize and cache all essential knowledge
     */
    async initializeCache() {
        console.log('[KnowledgeCache] Initializing cache...');

        if (!navigator.onLine) {
            console.log('[KnowledgeCache] Offline - using existing cache');
            return;
        }

        try {
            // Cache each category
            for (const category of this.categories) {
                try {
                    await this.cacheCategory(category);
                    console.log(`[KnowledgeCache] Cached ${category}`);
                } catch (error) {
                    console.warn(`[KnowledgeCache] Failed to cache ${category}:`, error);
                }

                // Small delay between requests
                await this.delay(100);
            }

            // Save cache version
            await this.storage.savePreference('knowledge-cache-version', this.cacheVersion);
            await this.storage.savePreference('knowledge-cache-date', Date.now());

            console.log('[KnowledgeCache] Cache initialization complete');
        } catch (error) {
            console.error('[KnowledgeCache] Cache initialization failed:', error);
        }
    }

    /**
     * Cache a specific category
     */
    async cacheCategory(category) {
        try {
            // Fetch data from API
            const response = await fetch(`/api/knowledge/${category}`);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();

            // Store in IndexedDB
            await this.storage.cacheKnowledge(category, data);

            return data;
        } catch (error) {
            console.error(`[KnowledgeCache] Failed to cache ${category}:`, error);
            throw error;
        }
    }

    /**
     * Get knowledge from cache or network
     */
    async getKnowledge(category, fallbackToCache = true) {
        try {
            // Try network first if online
            if (navigator.onLine) {
                try {
                    const networkData = await this.fetchFromNetwork(category);
                    if (networkData) {
                        // Update cache in background
                        this.storage.cacheKnowledge(category, networkData)
                            .catch(err => console.warn('[KnowledgeCache] Cache update failed:', err));
                        return networkData;
                    }
                } catch (networkError) {
                    console.warn(`[KnowledgeCache] Network fetch failed for ${category}:`, networkError);
                }
            }

            // Fallback to cache
            if (fallbackToCache) {
                const cachedData = await this.storage.getKnowledge(category);

                if (cachedData) {
                    console.log(`[KnowledgeCache] Using cached data for ${category}`);
                    return {
                        ...cachedData.data,
                        fromCache: true,
                        cacheDate: cachedData.lastUpdated
                    };
                }
            }

            return null;
        } catch (error) {
            console.error(`[KnowledgeCache] Failed to get knowledge for ${category}:`, error);
            return null;
        }
    }

    /**
     * Fetch knowledge from network
     */
    async fetchFromNetwork(category) {
        const response = await fetch(`/api/knowledge/${category}`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.json();
    }

    /**
     * Search cached knowledge
     */
    async search(query, categories = null) {
        const searchTerms = query.toLowerCase().split(' ').filter(term => term.length > 2);
        const results = [];

        // Get categories to search
        const categoriesToSearch = categories || this.categories;

        for (const category of categoriesToSearch) {
            try {
                const knowledge = await this.storage.getKnowledge(category);

                if (knowledge && knowledge.data) {
                    const matches = this.searchInData(knowledge.data, searchTerms);

                    matches.forEach(match => {
                        results.push({
                            category: category,
                            ...match,
                            relevance: match.score
                        });
                    });
                }
            } catch (error) {
                console.warn(`[KnowledgeCache] Search error in ${category}:`, error);
            }
        }

        // Sort by relevance
        results.sort((a, b) => b.relevance - a.relevance);

        return results;
    }

    /**
     * Search within data structure
     */
    searchInData(data, searchTerms) {
        const matches = [];

        const searchObject = (obj, path = []) => {
            if (typeof obj === 'string') {
                const text = obj.toLowerCase();
                let score = 0;

                searchTerms.forEach(term => {
                    if (text.includes(term)) {
                        score += 1;
                    }
                });

                if (score > 0) {
                    matches.push({
                        text: obj,
                        path: path.join('.'),
                        score: score
                    });
                }
            } else if (Array.isArray(obj)) {
                obj.forEach((item, index) => {
                    searchObject(item, [...path, index]);
                });
            } else if (typeof obj === 'object' && obj !== null) {
                Object.keys(obj).forEach(key => {
                    searchObject(obj[key], [...path, key]);
                });
            }
        };

        searchObject(data);
        return matches;
    }

    /**
     * Get crop information (specialized method)
     */
    async getCropInfo(cropName) {
        const crops = await this.getKnowledge('crops');

        if (!crops) {
            return null;
        }

        const cropData = crops.items || crops.crops || [];

        // Find matching crop (case-insensitive)
        const crop = cropData.find(c =>
            c.name.toLowerCase() === cropName.toLowerCase() ||
            (c.aliases && c.aliases.some(alias =>
                alias.toLowerCase() === cropName.toLowerCase()
            ))
        );

        return crop;
    }

    /**
     * Get disease information
     */
    async getDiseaseInfo(diseaseName) {
        const diseases = await this.getKnowledge('diseases');

        if (!diseases) {
            return null;
        }

        const diseaseData = diseases.items || diseases.diseases || [];

        // Find matching disease
        const disease = diseaseData.find(d =>
            d.name.toLowerCase() === diseaseName.toLowerCase()
        );

        return disease;
    }

    /**
     * Get best practices for a topic
     */
    async getBestPractices(topic) {
        const practices = await this.getKnowledge('best-practices');

        if (!practices) {
            return null;
        }

        const practiceData = practices.items || practices.practices || [];

        // Filter by topic
        const matchingPractices = practiceData.filter(p =>
            p.topic && p.topic.toLowerCase().includes(topic.toLowerCase())
        );

        return matchingPractices;
    }

    /**
     * Check if cache needs refresh
     */
    async needsRefresh() {
        try {
            const cacheDate = await this.storage.getPreference('knowledge-cache-date');
            const cacheVersion = await this.storage.getPreference('knowledge-cache-version');

            if (!cacheDate || !cacheVersion) {
                return true;
            }

            // Check if cache is older than 7 days
            const daysSinceCache = (Date.now() - cacheDate) / (1000 * 60 * 60 * 24);

            if (daysSinceCache > 7) {
                return true;
            }

            // Check if version has changed
            if (cacheVersion !== this.cacheVersion) {
                return true;
            }

            return false;
        } catch (error) {
            console.error('[KnowledgeCache] Error checking cache freshness:', error);
            return true;
        }
    }

    /**
     * Refresh cache in background
     */
    async refreshCache() {
        if (!navigator.onLine) {
            console.log('[KnowledgeCache] Cannot refresh - offline');
            return;
        }

        console.log('[KnowledgeCache] Refreshing cache...');

        try {
            await this.initializeCache();
            console.log('[KnowledgeCache] Cache refresh complete');
        } catch (error) {
            console.error('[KnowledgeCache] Cache refresh failed:', error);
        }
    }

    /**
     * Get cache statistics
     */
    async getStats() {
        const allKnowledge = await this.storage.getAllKnowledge();

        const stats = {
            categories: allKnowledge.length,
            totalItems: 0,
            oldestCache: null,
            newestCache: null,
            cacheVersion: await this.storage.getPreference('knowledge-cache-version'),
            cacheDate: await this.storage.getPreference('knowledge-cache-date')
        };

        allKnowledge.forEach(item => {
            // Count items if data is an array
            if (Array.isArray(item.data)) {
                stats.totalItems += item.data.length;
            } else if (item.data.items) {
                stats.totalItems += item.data.items.length;
            }

            // Track oldest and newest
            if (!stats.oldestCache || item.lastUpdated < stats.oldestCache) {
                stats.oldestCache = item.lastUpdated;
            }
            if (!stats.newestCache || item.lastUpdated > stats.newestCache) {
                stats.newestCache = item.lastUpdated;
            }
        });

        return stats;
    }

    /**
     * Preload essential data for offline use
     */
    async preloadEssentials() {
        const essentials = [
            'crops',
            'diseases',
            'best-practices',
            'seasonal-calendar'
        ];

        console.log('[KnowledgeCache] Preloading essentials...');

        const promises = essentials.map(category =>
            this.getKnowledge(category, false).catch(err =>
                console.warn(`[KnowledgeCache] Failed to preload ${category}:`, err)
            )
        );

        await Promise.all(promises);

        console.log('[KnowledgeCache] Essentials preloaded');
    }

    /**
     * Clear all cached knowledge
     */
    async clearCache() {
        console.log('[KnowledgeCache] Clearing cache...');

        for (const category of this.categories) {
            try {
                // Clear by setting expired data
                await this.storage.cacheKnowledge(category, null);
            } catch (error) {
                console.warn(`[KnowledgeCache] Failed to clear ${category}:`, error);
            }
        }

        await this.storage.savePreference('knowledge-cache-version', null);
        await this.storage.savePreference('knowledge-cache-date', null);

        console.log('[KnowledgeCache] Cache cleared');
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
    window.KnowledgeCache = KnowledgeCache;
}
