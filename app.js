/*
Government Scheme Awareness Portal - Main JavaScript
Hackathon Demo Application
*/

// Global State
let currentLanguage = localStorage.getItem('language') || 'en';
let userProfile = JSON.parse(localStorage.getItem('userProfile')) || null;
let currentSchemeId = null;
let isOnline = navigator.onLine;

// Translations
const translations = {
    en: {
        search: 'Search schemes...',
        category: 'Category',
        all: 'All',
        student: 'Student',
        farmer: 'Farmer',
        women: 'Women',
        housing: 'Housing',
        health: 'Health',
        employment: 'Employment',
        other: 'Other',
        filter: 'Filter',
        sort: 'Sort',
        byEligibility: 'By Eligibility',
        byDeadline: 'By Deadline',
        byBenefits: 'By Benefits',
        viewDetails: 'View Details',
        applyNow: 'Apply Now',
        saveScheme: 'Save Scheme',
        saved: 'Saved',
        checkEligibility: 'Check Eligibility',
        recommended: 'Recommended for You',
        deadlines: 'Upcoming Deadlines',
        benefits: 'Benefits',
        eligibility: 'Eligibility Criteria',
        documents: 'Required Documents',
        howToApply: 'How to Apply',
        officialWebsite: 'Apply on Official Website',
        eligible: 'Eligible',
        partiallyEligible: 'Partially Eligible',
        notEligible: 'Not Eligible',
        profileSetup: 'Profile Setup',
        name: 'Name',
        age: 'Age',
        incomeRange: 'Income Range',
        saveProfile: 'Save Profile',
        mySchemes: 'My Schemes',
        reminders: 'Reminders',
        addReminder: 'Add Reminder',
        noSchemes: 'No schemes found',
        noSavedSchemes: 'No saved schemes yet',
        noReminders: 'No reminders set',
        offlineMode: 'Offline mode: Showing basic data',
        loading: 'Loading...',
        chatbotTitle: 'Scheme Assistant',
        typeMessage: 'Type a message...',
        send: 'Send',
        quickSuggestions: {
            student: 'Student Schemes',
            farmer: 'Farmer Schemes',
            women: 'Women Schemes',
            housing: 'Housing Schemes'
        }
    },
    hi: {
        search: 'योजनाएं खोजें...',
        category: 'श्रेणी',
        all: 'सभी',
        student: 'छात्र',
        farmer: 'किसान',
        women: 'महिला',
        housing: 'आवास',
        health: 'स्वास्थ्य',
        employment: 'रोजगार',
        other: 'अन्य',
        filter: 'फ़िल्टर',
        sort: 'क्रमबद्ध करें',
        byEligibility: 'पात्रता के अनुसार',
        byDeadline: 'समय सीमा के अनुसार',
        byBenefits: 'लाभ के अनुसार',
        viewDetails: 'विवरण देखें',
        applyNow: 'अभी आवेदन करें',
        saveScheme: 'योजना सहेजें',
        saved: 'सहेजा गया',
        checkEligibility: 'पात्रता जांचें',
        recommended: 'आपके लिए अनुशंसित',
        deadlines: 'आगामी समय सीमा',
        benefits: 'लाभ',
        eligibility: 'पात्रता मानदंड',
        documents: 'आवश्यक दस्तावेज',
        howToApply: 'आवेदन कैसे करें',
        officialWebsite: 'आधिकारिक वेबसाइट पर आवेदन करें',
        eligible: 'पात्र',
        partiallyEligible: 'आंशिक पात्र',
        notEligible: 'अपात्र',
        profileSetup: 'प्रोफ़ाइल सेटअप',
        name: 'नाम',
        age: 'उम्र',
        incomeRange: 'आय सीमा',
        saveProfile: 'प्रोफ़ाइल सहेजें',
        mySchemes: 'मेरी योजनाएं',
        reminders: 'रिमाइंडर',
        addReminder: 'रिमाइंडर जोड़ें',
        noSchemes: 'कोई योजना नहीं मिली',
        noSavedSchemes: 'अभी तक कोई योजना सहेजी नहीं',
        noReminders: 'कोई रिमाइंडर सेट नहीं',
        offlineMode: 'ऑफलाइन मोड: बुनियादी डेटा दिखा रहा है',
        loading: 'लोड हो रहा है...',
        chatbotTitle: 'योजना सहायक',
        typeMessage: 'संदेश लिखें...',
        send: 'भेजें'
    },
    mr: {
        search: 'योजना शोधा...',
        category: 'श्रेणी',
        all: 'सर्व',
        student: 'विद्यार्थी',
        farmer: 'शेतकरी',
        women: 'महिला',
        housing: 'घर',
        health: 'आरोग्य',
        employment: 'रोजगार',
        other: 'इतर',
        filter: 'फिल्टर',
        sort: 'क्रमवार लावा',
        byEligibility: 'पात्रतेनुसार',
        byDeadline: 'मुदतीनुसार',
        byBenefits: 'लाभानुसार',
        viewDetails: 'तपशील पाहा',
        applyNow: 'आता अर्ज करा',
        saveScheme: 'योजना सेव्ह करा',
        saved: 'सेव्ह केले',
        checkEligibility: 'पात्रता तपासा',
        recommended: 'तुमच्यासाठी शिफारस केले',
        deadlines: 'आगामी मुदत',
        benefits: 'लाभ',
        eligibility: 'पात्रता निकष',
        documents: 'आवश्यक कागदपत्रे',
        howToApply: 'अर्ज कसा करावा',
        officialWebsite: 'अधिकृत वेबसाइटवर अर्ज करा',
        eligible: 'पात्र',
        partiallyEligible: 'अंशतः पात्र',
        notEligible: 'अपात्र',
        profileSetup: 'प्रोफाइल सेटअप',
        name: 'नाव',
        age: 'वय',
        incomeRange: 'उत्पन्न मर्यादा',
        saveProfile: 'प्रोफाइल सेव्ह करा',
        mySchemes: 'माझ्या योजना',
        reminders: 'स्मरणपत्रे',
        addReminder: 'स्मरणपत्र जोडा',
        noSchemes: 'योजना आढळली नाही',
        noSavedSchemes: 'अजून सेव्ह केलेल्या योजना नाहीत',
        noReminders: 'सेट केलेली स्मरणपत्रे नाहीत',
        offlineMode: 'ऑफलाइन मोड: मूलभूत डेटा दाखवित आहे',
        loading: 'लोड होत आहे...',
        chatbotTitle: 'योजना सहाय्यक',
        typeMessage: 'संदेश लिहा...',
        send: 'पाठवा'
    }
};

// Initialize App
document.addEventListener('DOMContentLoaded', function() {
    initApp();
});

function initApp() {
    // Check online status
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    // Check login status and update UI
    checkLoginStatus();
    
    // Load language
    updateLanguage(currentLanguage);
    
    // Initialize page-specific functionality
    const currentPage = getCurrentPage();
    
    switch(currentPage) {
        case 'index':
            initDashboard();
            break;
        case 'profile':
            initProfile();
            break;
        case 'schemes':
            initSchemes();
            break;
        case 'scheme-detail':
            initSchemeDetail();
            break;
        case 'saved-schemes':
            initSavedSchemes();
            break;
    }
    
    // Initialize chatbot
    initChatbot();
}

function getCurrentPage() {
    const path = window.location.pathname;
    if (path.includes('profile')) return 'profile';
    if (path.includes('scheme-detail')) return 'scheme-detail';
    if (path.includes('saved-schemes')) return 'saved-schemes';
    if (path.includes('schemes')) return 'schemes';
    return 'index';
}

// Online/Offline Handling
function updateOnlineStatus() {
    isOnline = navigator.onLine;
    const banner = document.getElementById('offlineBanner');
    if (banner) {
        banner.classList.toggle('active', !isOnline);
    }
}

// Language Functions
function changeLanguage(lang) {
    currentLanguage = lang;
    localStorage.setItem('language', lang);
    updateLanguage(lang);
    
    // Update active button
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });
    
    // Refresh current page
    location.reload();
}

function updateLanguage(lang) {
    const t = translations[lang] || translations.en;
    
    // Update all translatable elements
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.dataset.i18n;
        if (t[key]) {
            el.textContent = t[key];
        }
    });
    
    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.dataset.i18nPlaceholder;
        if (t[key]) {
            el.placeholder = t[key];
        }
    });
}

// Dashboard Functions
async function initDashboard() {
    loadUserProfile();
    
    // Load schemes
    await loadNewSchemes();
    await loadRecommendedSchemes();
    await loadDeadlines();
    
    // Setup category cards
    setupCategoryCards();
}

function loadUserProfile() {
    userProfile = JSON.parse(localStorage.getItem('userProfile'));
    if (userProfile) {
        updateProfileDisplay();
    }
}

function updateProfileDisplay() {
    const profileIndicator = document.getElementById('profileIndicator');
    if (profileIndicator && userProfile) {
        profileIndicator.textContent = `👤 ${userProfile.name || 'User'}`;
    }
}

async function loadRecommendedSchemes() {
    const container = document.getElementById('recommendedSchemes');
    if (!container) return;
    
    showLoading(container);
    
    try {
        let schemes;
        
        if (userProfile && userProfile.category) {
            // Get personalized recommendations
            const response = await fetch('/api/recommendations', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ profile: userProfile })
            });
            schemes = await response.json();
        } else {
            // Get all schemes
            const response = await fetch('/api/schemes');
            schemes = await response.json();
            schemes = schemes.slice(0, 6); // Limit to 6
        }
        
        displaySchemes(container, schemes);
    } catch (error) {
        console.error('Error loading schemes:', error);
        showError(container, 'Failed to load schemes');
    }
}

async function loadNewSchemes() {
    const container = document.getElementById('newSchemes');
    if (!container) return;
    
    try {
        const response = await fetch('/api/new-schemes');
        const schemes = await response.json();
        
        displaySchemes(container, schemes);
    } catch (error) {
        console.error('Error loading new schemes:', error);
    }
}

async function loadDeadlines() {
    const container = document.getElementById('deadlinesList');
    if (!container) return;
    
    try {
        const response = await fetch('/api/deadlines');
        const schemes = await response.json();
        
        displayDeadlineSchemes(container, schemes);
    } catch (error) {
        console.error('Error loading deadlines:', error);
    }
}

function setupCategoryCards() {
    const cards = document.querySelectorAll('.category-card');
    cards.forEach(card => {
        card.addEventListener('click', () => {
            const category = card.dataset.category;
            window.location.href = `/schemes?category=${category}`;
        });
    });
}

// Scheme Display Functions
function displaySchemes(container, schemes) {
    if (!schemes || schemes.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <p class="empty-state-text">${translations[currentLanguage].noSchemes}</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = schemes.map(scheme => createSchemeCard(scheme)).join('');
    
    // Add event listeners
    container.querySelectorAll('.view-details-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const schemeId = e.target.closest('.scheme-card').dataset.schemeId;
            window.location.href = `/scheme-detail?id=${schemeId}`;
        });
    });
    
    container.querySelectorAll('.save-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const schemeId = e.target.closest('.scheme-card').dataset.schemeId;
            saveScheme(schemeId, e.target);
        });
    });
}

function createSchemeCard(scheme) {
    const lang = currentLanguage;
    const name = scheme[`name_${lang}`] || scheme.name;
    const description = scheme[`description_${lang}`] || scheme.description;
    const benefits = scheme[`benefits_${lang}`] || scheme.benefits;
    
    const categoryIcons = {
        student: '🎓',
        farmer: '🚜',
        women: '👩',
        housing: '🏠',
        health: '❤️',
        employment: '💼',
        other: '📋'
    };
    
    const categoryLabels = {
        student: translations[lang].student,
        farmer: translations[lang].farmer,
        women: translations[lang].women,
        housing: translations[lang].housing,
        health: translations[lang].health,
        employment: translations[lang].employment,
        other: translations[lang].other
    };
    
    return `
        <div class="scheme-card" data-scheme-id="${scheme.id}">
            <span class="scheme-category-badge">${categoryIcons[scheme.category] || '📋'} ${categoryLabels[scheme.category] || scheme.category}</span>
            <h3 class="scheme-name">${name}</h3>
            <p class="scheme-description">${description}</p>
            ${scheme.deadline ? `
                <div class="scheme-deadline">
                    📅 ${formatDate(scheme.deadline)}
                </div>
            ` : ''}
            <div class="scheme-actions">
                <button class="btn btn-primary btn-sm view-details-btn">
                    ${translations[lang].viewDetails}
                </button>
                <button class="btn btn-outline btn-sm save-btn">
                    ${translations[lang].saveScheme}
                </button>
            </div>
        </div>
    `;
}

function displayDeadlineSchemes(container, schemes) {
    if (!schemes || schemes.length === 0) {
        container.innerHTML = `<p>${translations[currentLanguage].noSchemes}</p>`;
        return;
    }
    
    const lang = currentLanguage;
    
    container.innerHTML = schemes.map(scheme => {
        const name = scheme[`name_${lang}`] || scheme.name;
        return `
            <div class="reminder-card">
                <div class="reminder-info">
                    <h4>${name}</h4>
                    <span class="reminder-date">📅 ${formatDate(scheme.deadline)}</span>
                </div>
                <a href="/scheme-detail?id=${scheme.id}" class="btn btn-orange btn-sm">
                    ${translations[lang].viewDetails}
                </a>
            </div>
        `;
    }).join('');
}

// Profile Functions
function initProfile() {
    // Load existing profile if any
    if (userProfile) {
        document.getElementById('nameInput').value = userProfile.name || '';
        document.getElementById('categoryInput').value = userProfile.category || '';
        document.getElementById('ageInput').value = userProfile.age || '';
        document.getElementById('incomeInput').value = userProfile.income_range || '';
    }
    
    // Setup form submission
    const form = document.getElementById('profileForm');
    if (form) {
        form.addEventListener('submit', saveUserProfile);
    }
}

function saveUserProfile(e) {
    e.preventDefault();
    
    const profile = {
        name: document.getElementById('nameInput').value,
        category: document.getElementById('categoryInput').value,
        age: parseInt(document.getElementById('ageInput').value) || 0,
        income_range: document.getElementById('incomeInput').value,
        gender: document.getElementById('genderInput') ? document.getElementById('genderInput').value : 'All'
    };
    
    userProfile = profile;
    localStorage.setItem('userProfile', JSON.stringify(profile));
    
    showToast(translations[currentLanguage].saved, 'success');
    
    // Redirect to dashboard after short delay
    setTimeout(() => {
        window.location.href = '/';
    }, 1000);
}

// Schemes Page Functions
async function initSchemes() {
    const params = new URLSearchParams(window.location.search);
    const category = params.get('category') || 'all';
    
    // Set filter values
    const categoryFilter = document.getElementById('categoryFilter');
    if (categoryFilter) {
        categoryFilter.value = category;
    }
    
    // Setup event listeners
    setupSchemeFilters();
    
    // Load schemes
    await loadAllSchemes();
}

async function loadAllSchemes() {
    const container = document.getElementById('schemesContainer');
    if (!container) return;
    
    showLoading(container);
    
    try {
        const params = new URLSearchParams();
        
        const categoryFilter = document.getElementById('categoryFilter');
        const searchInput = document.getElementById('searchInput');
        const incomeFilter = document.getElementById('incomeFilter');
        
        if (categoryFilter && categoryFilter.value !== 'all') {
            params.append('category', categoryFilter.value);
        }
        
        if (searchInput && searchInput.value) {
            params.append('search', searchInput.value);
        }
        
        if (incomeFilter && incomeFilter.value !== 'all') {
            params.append('income_range', incomeFilter.value);
        }
        
        const response = await fetch(`/api/schemes?${params.toString()}`);
        const schemes = await response.json();
        
        displaySchemes(container, schemes);
    } catch (error) {
        console.error('Error loading schemes:', error);
        showError(container, 'Failed to load schemes');
    }
}

function setupSchemeFilters() {
    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(loadAllSchemes, 500));
    }
    
    // Filters - including state filter
    const filters = ['categoryFilter', 'incomeFilter', 'stateFilter'];
    filters.forEach(filterId => {
        const filter = document.getElementById(filterId);
        if (filter) {
            filter.addEventListener('change', loadAllSchemes);
        }
    });
    
    // Sort
    const sortSelect = document.getElementById('sortSelect');
    if (sortSelect) {
        sortSelect.addEventListener('change', () => {
            sortSchemes(sortSelect.value);
        });
    }
}

function sortSchemes(sortBy) {
    const container = document.getElementById('schemesContainer');
    const cards = Array.from(container.querySelectorAll('.scheme-card'));
    
    cards.sort((a, b) => {
        const schemeIdA = a.dataset.schemeId;
        const schemeIdB = b.dataset.schemeId;
        
        // This would require fetching scheme data, simplified for demo
        return 0;
    });
    
    container.innerHTML = '';
    cards.forEach(card => container.appendChild(card));
}

// Scheme Detail Functions
async function initSchemeDetail() {
    const params = new URLSearchParams(window.location.search);
    currentSchemeId = params.get('id');
    
    if (!currentSchemeId) {
        window.location.href = '/schemes';
        return;
    }
    
    await loadSchemeDetails();
    setupEligibilityChecker();
}

async function loadSchemeDetails() {
    const container = document.getElementById('detailContainer');
    if (!container) return;
    
    showLoading(container);
    
    try {
        const response = await fetch(`/api/scheme/${currentSchemeId}`);
        const scheme = await response.json();
        
        displaySchemeDetails(container, scheme);
    } catch (error) {
        console.error('Error loading scheme:', error);
        showError(container, 'Failed to load scheme details');
    }
}

function displaySchemeDetails(container, scheme) {
    const lang = currentLanguage;
    const name = scheme[`name_${lang}`] || scheme.name;
    const description = scheme[`description_${lang}`] || scheme.description;
    const benefits = scheme[`benefits_${lang}`] || scheme.benefits;
    const eligibility = scheme[`eligibility_${lang}`] || scheme.eligibility;
    const documents = scheme[`documents_${lang}`] || scheme.documents;
    const howToApply = scheme[`how_to_apply_${lang}`] || scheme.how_to_apply;
    
    const categoryLabels = {
        student: translations[lang].student,
        farmer: translations[lang].farmer,
        women: translations[lang].women,
        housing: translations[lang].housing,
        health: translations[lang].health,
        employment: translations[lang].employment,
        other: translations[lang].other
    };
    
    container.innerHTML = `
        <div class="detail-header">
            <span class="detail-category">${categoryLabels[scheme.category] || scheme.category}</span>
            <h1 class="detail-title">${name}</h1>
            <p>${description}</p>
            ${scheme.deadline ? `
                <div class="detail-deadline mt-2">
                    📅 Last Date: ${formatDate(scheme.deadline)}
                </div>
            ` : ''}
        </div>
        
        <div class="detail-section">
            <h2 class="detail-section-title">💰 ${translations[lang].benefits}</h2>
            <ul class="benefits-list">
                ${benefits.split(',').map(b => `<li>${b.trim()}</li>`).join('')}
            </ul>
        </div>
        
        <div class="detail-section">
            <h2 class="detail-section-title">✓ ${translations[lang].eligibility}</h2>
            <ul class="eligibility-list">
                ${eligibility.split(',').map(e => `<li>${e.trim()}</li>`).join('')}
            </ul>
        </div>
        
        <div class="detail-section">
            <h2 class="detail-section-title">📄 ${translations[lang].documents}</h2>
            <ul class="documents-list">
                ${documents.split(',').map(d => `<li>${d.trim()}</li>`).join('')}
            </ul>
        </div>
        
        <div class="detail-section">
            <h2 class="detail-section-title">📝 ${translations[lang].howToApply}</h2>
            <ol class="steps-list">
                ${howToApply.split('\n').filter(s => s.trim()).map(s => `<li>${s.replace(/^\d+\.\s*/, '').trim()}</li>`).join('')}
            </ol>
        </div>
        
        <div class="detail-section">
            <h2 class="detail-section-title">🎯 ${translations[lang].checkEligibility}</h2>
            <div id="eligibilityResult"></div>
            <button class="btn btn-primary" onclick="checkMyEligibility()">
                ${translations[lang].checkEligibility}
            </button>
        </div>
        
        <div class="detail-section" style="text-align: center;">
            <a href="${scheme.official_link}" target="_blank" class="btn btn-orange">
                🌐 ${translations[lang].officialWebsite}
            </a>
            <button class="btn btn-green ml-2" onclick="saveThisScheme()">
                ❤️ ${translations[lang].saveScheme}
            </button>
        </div>
    `;
}

async function checkMyEligibility() {
    if (!userProfile) {
        showToast('Please set up your profile first', 'error');
        setTimeout(() => window.location.href = '/profile', 1500);
        return;
    }
    
    const resultContainer = document.getElementById('eligibilityResult');
    showLoading(resultContainer);
    
    try {
        const response = await fetch('/api/check-eligibility', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                profile: userProfile,
                scheme_id: currentSchemeId
            })
        });
        
        const result = await response.json();
        
        let statusClass = 'not-eligible';
        let statusText = translations[currentLanguage].notEligible;
        
        if (result.eligible) {
            statusClass = 'eligible';
            statusText = translations[currentLanguage].eligible;
        } else if (result.reasons && result.reasons.length > 0) {
            statusClass = 'partial';
            statusText = translations[currentLanguage].partiallyEligible;
        }
        
        resultContainer.innerHTML = `
            <div class="eligibility-result ${statusClass}">
                <div class="eligibility-status">${statusText}</div>
                ${result.reasons && result.reasons.length > 0 ? `
                    <p>${result.reasons.join(', ')}</p>
                ` : ''}
            </div>
        `;
    } catch (error) {
        console.error('Error checking eligibility:', error);
        resultContainer.innerHTML = '<p class="error">Failed to check eligibility</p>';
    }
}

function saveThisScheme() {
    const sessionId = localStorage.getItem('sessionId') || generateSessionId();
    localStorage.setItem('sessionId', sessionId);
    
    fetch('/api/save-scheme', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            scheme_id: currentSchemeId
        })
    })
    .then(res => res.json())
    .then(data => {
        showToast(translations[currentLanguage].saved, 'success');
    })
    .catch(err => {
        showToast('Failed to save scheme', 'error');
    });
}

// Saved Schemes Functions
async function initSavedSchemes() {
    const sessionId = localStorage.getItem('sessionId') || generateSessionId();
    localStorage.setItem('sessionId', sessionId);
    
    await loadSavedSchemes();
    await loadReminders();
}

async function loadSavedSchemes() {
    const container = document.getElementById('savedSchemesContainer');
    if (!container) return;
    
    const sessionId = localStorage.getItem('sessionId');
    
    showLoading(container);
    
    try {
        const response = await fetch(`/api/saved-schemes?session_id=${sessionId}`);
        const schemes = await response.json();
        
        displaySchemes(container, schemes);
        
        // Update saved count
        const savedCount = document.getElementById('savedCount');
        if (savedCount) {
            savedCount.textContent = schemes.length;
        }
    } catch (error) {
        console.error('Error loading saved schemes:', error);
        showError(container, 'Failed to load saved schemes');
    }
}

async function loadReminders() {
    const container = document.getElementById('remindersContainer');
    if (!container) return;
    
    const sessionId = localStorage.getItem('sessionId');
    
    try {
        const response = await fetch(`/api/reminders?session_id=${sessionId}`);
        const reminders = await response.json();
        
        displayReminders(container, reminders);
    } catch (error) {
        console.error('Error loading reminders:', error);
    }
}

function displayReminders(container, reminders) {
    const lang = currentLanguage;
    
    if (!reminders || reminders.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">🔔</div>
                <p class="empty-state-text">${translations[lang].noReminders}</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = reminders.map(reminder => `
        <div class="reminder-card">
            <div class="reminder-info">
                <h4>${reminder.name}</h4>
                <span class="reminder-date">📅 Deadline: ${formatDate(reminder.deadline)}</span>
            </div>
            <div>
                <a href="/scheme-detail?id=${reminder.scheme_id}" class="btn btn-orange btn-sm">
                    ${translations[lang].viewDetails}
                </a>
            </div>
        </div>
    `).join('');
}

function addReminder(schemeId) {
    const sessionId = localStorage.getItem('sessionId');
    const reminderDate = prompt('Enter reminder date (YYYY-MM-DD):');
    
    if (!reminderDate) return;
    
    fetch('/api/add-reminder', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            scheme_id: schemeId,
            reminder_date: reminderDate
        })
    })
    .then(res => res.json())
    .then(data => {
        showToast('Reminder added!', 'success');
        loadReminders();
    });
}

// Chatbot Functions
function initChatbot() {
    const toggleBtn = document.getElementById('chatbotToggle');
    const panel = document.getElementById('chatbotPanel');
    const closeBtn = document.getElementById('chatbotClose');
    const sendBtn = document.getElementById('chatbotSend');
    const input = document.getElementById('chatbotInput');
    
    if (!toggleBtn || !panel) return;
    
    // Toggle chatbot
    toggleBtn.addEventListener('click', () => {
        panel.classList.toggle('active');
        if (panel.classList.contains('active')) {
            input.focus();
        }
    });
    
    // Close chatbot
    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            panel.classList.remove('active');
        });
    }
    
    // Send message
    const sendMessage = () => {
        const message = input.value.trim();
        if (!message) return;
        
        addUserMessage(message);
        input.value = '';
        
        // Show typing indicator
        showTypingIndicator();
        
        // Send to API
        sendToChatbot(message);
    };
    
    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }
    
    if (input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }
    
    // Quick suggestions
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const suggestion = btn.textContent;
            addUserMessage(suggestion);
            showTypingIndicator();
            sendToChatbot(suggestion);
        });
    });
}

function addUserMessage(text) {
    const container = document.getElementById('chatbotMessages');
    if (!container) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message user';
    messageDiv.textContent = text;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function addBotMessage(text) {
    const container = document.getElementById('chatbotMessages');
    if (!container) return;
    
    // Remove typing indicator
    const typing = container.querySelector('.chatbot-typing');
    if (typing) typing.remove();
    
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message bot';
    messageDiv.textContent = text;
    container.appendChild(messageDiv);
    container.scrollTop = container.scrollHeight;
}

function showTypingIndicator() {
    const container = document.getElementById('chatbotMessages');
    if (!container) return;
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chatbot-typing active';
    typingDiv.innerHTML = `
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
    `;
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
}

async function sendToChatbot(message) {
    try {
        const response = await fetch('/api/chatbot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                language: currentLanguage,
                category: userProfile ? userProfile.category : ''
            })
        });
        
        const data = await response.json();
        
        // Simulate delay for realism
        setTimeout(() => {
            addBotMessage(data.response);
        }, 500);
    } catch (error) {
        console.error('Chatbot error:', error);
        
        // Remove typing and show error
        const container = document.getElementById('chatbotMessages');
        const typing = container.querySelector('.chatbot-typing');
        if (typing) typing.remove();
        
        addBotMessage('Sorry, I encountered an error. Please try again.');
    }
}

// Save Scheme Function
function saveScheme(schemeId, button) {
    const sessionId = localStorage.getItem('sessionId') || generateSessionId();
    localStorage.setItem('sessionId', sessionId);
    
    fetch('/api/save-scheme', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: sessionId,
            scheme_id: schemeId
        })
    })
    .then(res => res.json())
    .then(data => {
        button.textContent = translations[currentLanguage].saved;
        button.disabled = true;
        showToast(translations[currentLanguage].saved, 'success');
    })
    .catch(err => {
        showToast('Failed to save', 'error');
    });
}

// Utility Functions
function generateSessionId() {
    return 'user_' + Math.random().toString(36).substr(2, 9);
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' });
}

function showLoading(container) {
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;
}

function showError(container, message) {
    container.innerHTML = `
        <div class="empty-state">
            <div class="empty-state-icon">⚠️</div>
            <p class="empty-state-text">${message}</p>
        </div>
    `;
}

function showToast(message, type = '') {
    let toast = document.querySelector('.toast');
    if (!toast) {
        toast = document.createElement('div');
        toast.className = 'toast';
        document.body.appendChild(toast);
    }
    
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Global functions for inline event handlers
window.changeLanguage = changeLanguage;
window.checkMyEligibility = checkMyEligibility;
window.saveThisScheme = saveThisScheme;
window.addReminder = addReminder;
window.logout = logout;

// Logout Function
function logout() {
    // Clear local storage
    localStorage.removeItem('userProfile');
    localStorage.removeItem('sessionId');
    userProfile = null;
    
    // Show toast
    showToast('Logged out successfully!', 'success');
    
    // Redirect to login page after short delay
    setTimeout(() => {
        window.location.href = '/login';
    }, 1000);
}

// Check if user is logged in and update UI
function checkLoginStatus() {
    const logoutBtn = document.getElementById('logoutBtn');
    
    // Check for userProfile in localStorage (set after login)
    const storedProfile = localStorage.getItem('userProfile');
    
    if (storedProfile) {
        userProfile = JSON.parse(storedProfile);
        
        // Show logout button
        if (logoutBtn) {
            logoutBtn.style.display = 'flex';
        }
        
        // Update profile indicator
        const profileIndicator = document.getElementById('profileIndicator');
        if (profileIndicator) {
            profileIndicator.textContent = `👤 ${userProfile.name || 'User'}`;
        }
    } else {
        // Hide logout button
        if (logoutBtn) {
            logoutBtn.style.display = 'none';
        }
    }
}
