/**
 * Offline Functionality Diagnostic Script
 * Run this in browser console to check offline setup
 *
 * Usage: Copy this entire file and paste in Console, then press Enter
 */

(async function diagnosticTest() {
    console.log('🔍 AgriBot Offline Diagnostic Starting...\n');
    console.log('=' .repeat(60));

    const results = {
        passed: [],
        failed: [],
        warnings: []
    };

    // Test 1: HTTPS Check
    console.log('\n📋 Test 1: HTTPS Check');
    if (window.location.protocol === 'https:' || window.location.hostname === 'localhost') {
        console.log('✅ PASS: Using HTTPS or localhost');
        results.passed.push('HTTPS/localhost');
    } else {
        console.log('❌ FAIL: Not using HTTPS (service workers require HTTPS!)');
        results.failed.push('HTTPS required');
    }

    // Test 2: Service Worker Support
    console.log('\n📋 Test 2: Service Worker Browser Support');
    if ('serviceWorker' in navigator) {
        console.log('✅ PASS: Browser supports service workers');
        results.passed.push('Service Worker support');
    } else {
        console.log('❌ FAIL: Browser does NOT support service workers');
        results.failed.push('Service Worker support');
        console.log('   Try using Chrome, Firefox, or Edge');
    }

    // Test 3: Service Worker Registration
    console.log('\n📋 Test 3: Service Worker Registration');
    try {
        const registrations = await navigator.serviceWorker.getRegistrations();

        if (registrations.length === 0) {
            console.log('❌ FAIL: No service worker registered');
            console.log('   Service worker should auto-register on page load');
            results.failed.push('Service Worker registration');
        } else {
            console.log(`✅ PASS: ${registrations.length} service worker(s) registered`);
            registrations.forEach((reg, i) => {
                console.log(`   ${i + 1}. Scope: ${reg.scope}`);
                console.log(`      State: ${reg.active?.state || 'not active'}`);
            });
            results.passed.push('Service Worker registration');
        }
    } catch (error) {
        console.log('❌ FAIL: Error checking service workers:', error.message);
        results.failed.push('Service Worker check');
    }

    // Test 4: Service Worker File Accessibility
    console.log('\n📋 Test 4: Service Worker File Accessibility');
    try {
        const swUrl = `${window.location.origin}/service-worker.js`;
        const response = await fetch(swUrl);

        if (response.ok) {
            console.log('✅ PASS: service-worker.js is accessible');
            console.log(`   URL: ${swUrl}`);
            console.log(`   Status: ${response.status}`);
            results.passed.push('Service Worker file');
        } else {
            console.log(`❌ FAIL: service-worker.js returned ${response.status}`);
            results.failed.push('Service Worker file');
        }
    } catch (error) {
        console.log('❌ FAIL: Cannot fetch service-worker.js:', error.message);
        results.failed.push('Service Worker file');
    }

    // Test 5: PWA Manifest
    console.log('\n📋 Test 5: PWA Manifest');
    try {
        const manifestUrl = `${window.location.origin}/manifest.json`;
        const response = await fetch(manifestUrl);

        if (response.ok) {
            console.log('✅ PASS: manifest.json is accessible');
            const manifest = await response.json();
            console.log(`   App Name: ${manifest.name || 'N/A'}`);
            results.passed.push('PWA Manifest');
        } else {
            console.log(`⚠️  WARNING: manifest.json returned ${response.status}`);
            console.log('   This is optional but recommended for PWA');
            results.warnings.push('PWA Manifest');
        }
    } catch (error) {
        console.log('⚠️  WARNING: Cannot fetch manifest.json:', error.message);
        results.warnings.push('PWA Manifest');
    }

    // Test 6: IndexedDB Support
    console.log('\n📋 Test 6: IndexedDB Support');
    if ('indexedDB' in window) {
        console.log('✅ PASS: Browser supports IndexedDB');
        results.passed.push('IndexedDB support');

        try {
            const dbs = await indexedDB.databases();
            const agribotDb = dbs.find(db => db.name === 'AgribotDB');

            if (agribotDb) {
                console.log('✅ PASS: AgribotDB exists');
                console.log(`   Version: ${agribotDb.version}`);
                results.passed.push('AgribotDB');
            } else {
                console.log('⚠️  WARNING: AgribotDB not found');
                console.log('   It will be created on first use');
                results.warnings.push('AgribotDB');
            }
        } catch (error) {
            console.log('⚠️  WARNING: Cannot list databases:', error.message);
        }
    } else {
        console.log('❌ FAIL: Browser does NOT support IndexedDB');
        results.failed.push('IndexedDB support');
    }

    // Test 7: Cache Storage
    console.log('\n📋 Test 7: Cache Storage');
    try {
        const cacheNames = await caches.keys();
        const agribotCaches = cacheNames.filter(name => name.startsWith('agribot-'));

        if (agribotCaches.length === 0) {
            console.log('⚠️  WARNING: No AgriBot caches found');
            console.log('   Caches will be created after service worker installs');
            results.warnings.push('Cache Storage');
        } else {
            console.log(`✅ PASS: ${agribotCaches.length} AgriBot cache(s) found:`);
            for (const cacheName of agribotCaches) {
                const cache = await caches.open(cacheName);
                const keys = await cache.keys();
                console.log(`   - ${cacheName}: ${keys.length} items`);
            }
            results.passed.push('Cache Storage');
        }
    } catch (error) {
        console.log('❌ FAIL: Error checking caches:', error.message);
        results.failed.push('Cache Storage');
    }

    // Test 8: Online Status Detection
    console.log('\n📋 Test 8: Online Status Detection');
    console.log(`   navigator.onLine: ${navigator.onLine}`);
    if (navigator.onLine) {
        console.log('✅ Browser thinks you are ONLINE');
    } else {
        console.log('⚠️  Browser thinks you are OFFLINE');
    }
    results.passed.push('Online detection');

    // Test 9: Offline Scripts Loaded
    console.log('\n📋 Test 9: Offline Scripts Loaded');

    if (typeof offlineStorage !== 'undefined') {
        console.log('✅ PASS: offlineStorage loaded');
        results.passed.push('offlineStorage script');
    } else {
        console.log('❌ FAIL: offlineStorage NOT loaded');
        results.failed.push('offlineStorage script');
    }

    if (typeof MessageQueue !== 'undefined') {
        console.log('✅ PASS: MessageQueue loaded');
        results.passed.push('MessageQueue script');
    } else {
        console.log('❌ FAIL: MessageQueue NOT loaded');
        results.failed.push('MessageQueue script');
    }

    if (typeof KnowledgeCache !== 'undefined') {
        console.log('✅ PASS: KnowledgeCache loaded');
        results.passed.push('KnowledgeCache script');
    } else {
        console.log('❌ FAIL: KnowledgeCache NOT loaded');
        results.failed.push('KnowledgeCache script');
    }

    // Test 10: Offline Initialization
    console.log('\n📋 Test 10: Offline System Initialization');

    if (typeof messageQueue !== 'undefined' && messageQueue !== null) {
        console.log('✅ PASS: messageQueue initialized');
        try {
            const queueSize = await messageQueue.getQueueSize();
            console.log(`   Queue size: ${queueSize}`);
        } catch (e) {
            console.log('   Queue size: unavailable');
        }
        results.passed.push('messageQueue initialization');
    } else {
        console.log('⚠️  WARNING: messageQueue not initialized yet');
        console.log('   Should initialize on DOMContentLoaded');
        results.warnings.push('messageQueue initialization');
    }

    if (typeof offlineStorage !== 'undefined' && offlineStorage.db) {
        console.log('✅ PASS: offlineStorage initialized (IndexedDB ready)');
        results.passed.push('offlineStorage initialization');
    } else {
        console.log('⚠️  WARNING: offlineStorage IndexedDB not ready');
        results.warnings.push('offlineStorage initialization');
    }

    // Test 11: Knowledge API Endpoints
    console.log('\n📋 Test 11: Knowledge API Endpoints');
    const endpoints = [
        '/api/knowledge/crops',
        '/api/knowledge/diseases',
        '/api/knowledge/best-practices'
    ];

    let endpointsPassed = 0;
    for (const endpoint of endpoints) {
        try {
            const response = await fetch(endpoint);
            if (response.ok) {
                console.log(`✅ ${endpoint}: OK`);
                endpointsPassed++;
            } else {
                console.log(`❌ ${endpoint}: ${response.status}`);
            }
        } catch (error) {
            console.log(`❌ ${endpoint}: ${error.message}`);
        }
    }

    if (endpointsPassed === endpoints.length) {
        console.log('✅ PASS: All knowledge endpoints accessible');
        results.passed.push('Knowledge API endpoints');
    } else if (endpointsPassed > 0) {
        console.log(`⚠️  WARNING: Only ${endpointsPassed}/${endpoints.length} endpoints working`);
        results.warnings.push('Knowledge API endpoints');
    } else {
        console.log('❌ FAIL: No knowledge endpoints accessible');
        results.failed.push('Knowledge API endpoints');
    }

    // Summary
    console.log('\n' + '='.repeat(60));
    console.log('📊 DIAGNOSTIC SUMMARY\n');

    console.log(`✅ Passed: ${results.passed.length} tests`);
    if (results.passed.length > 0) {
        results.passed.forEach(test => console.log(`   - ${test}`));
    }

    console.log(`\n⚠️  Warnings: ${results.warnings.length} tests`);
    if (results.warnings.length > 0) {
        results.warnings.forEach(test => console.log(`   - ${test}`));
    }

    console.log(`\n❌ Failed: ${results.failed.length} tests`);
    if (results.failed.length > 0) {
        results.failed.forEach(test => console.log(`   - ${test}`));
    }

    // Recommendations
    console.log('\n' + '='.repeat(60));
    console.log('💡 RECOMMENDATIONS\n');

    if (results.failed.length === 0 && results.warnings.length <= 3) {
        console.log('🎉 Excellent! Offline functionality should work.');
        console.log('\nTo test:');
        console.log('1. Make sure you\'re viewing this page ONLINE right now');
        console.log('2. Wait 30 seconds for caching to complete');
        console.log('3. Go to Network tab → Set to "Offline"');
        console.log('4. Try sending a message');
        console.log('5. You should see the queue indicator appear');
    } else if (results.failed.length > 0) {
        console.log('⚠️  Issues detected that need to be fixed:\n');

        if (results.failed.includes('HTTPS required')) {
            console.log('🔧 FIX: Access site via HTTPS');
            console.log('   Service workers require HTTPS (except localhost)');
        }

        if (results.failed.includes('Service Worker registration')) {
            console.log('🔧 FIX: Service worker not registering');
            console.log('   1. Check console for error messages');
            console.log('   2. Verify /service-worker.js is accessible');
            console.log('   3. Try hard refresh: Ctrl+Shift+R');
        }

        if (results.failed.includes('Service Worker file')) {
            console.log('🔧 FIX: Service worker file not accessible');
            console.log('   1. Check Flask routes in app/main.py');
            console.log('   2. Ensure /service-worker.js route exists');
            console.log('   3. Redeploy application');
        }

        if (results.failed.some(f => f.includes('script'))) {
            console.log('🔧 FIX: Offline scripts not loading');
            console.log('   1. Check <script> tags in chatbot.html');
            console.log('   2. Verify files exist in static/js/');
            console.log('   3. Check browser console for 404 errors');
        }

        if (results.failed.includes('Knowledge API endpoints')) {
            console.log('🔧 FIX: API endpoints not accessible');
            console.log('   1. Check app/routes/api.py has knowledge endpoints');
            console.log('   2. Ensure API blueprint is registered');
            console.log('   3. Test endpoints directly in browser');
        }
    } else {
        console.log('✅ Setup looks good! A few warnings are normal.');
        console.log('\nJust make sure to:');
        console.log('1. Visit the site ONLINE first (you are now)');
        console.log('2. Wait 30-60 seconds for caching');
        console.log('3. Then test offline mode');
    }

    console.log('\n' + '='.repeat(60));
    console.log('For detailed troubleshooting, see: RENDER_OFFLINE_DIAGNOSTIC.md');
    console.log('=' + '='.repeat(60) + '\n');

    return {
        passed: results.passed.length,
        warnings: results.warnings.length,
        failed: results.failed.length,
        details: results
    };
})();
