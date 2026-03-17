/**
 * eMuhasebe Pro - Veritabanı Soyutlama Katmanı
 * Firebase bağlantısı varsa Firebase kullan, yoksa localStorage (SQLite benzeri)
 * Manuel mod değiştirme desteklenir
 * Otomatik senkronizasyon ve toast bildirimleri
 */

// ==================== TOAST BİLDİRİM SİSTEMİ ====================
const Toast = {
    container: null,
    
    init() {
        if (this.container) return;
        
        // Toast container oluştur
        this.container = document.createElement('div');
        this.container.id = 'toast-container';
        this.container.style.cssText = `
            position: fixed;
            top: 1rem;
            right: 1rem;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
            max-width: 380px;
        `;
        document.body.appendChild(this.container);
    },
    
    show(message, type = 'info', duration = 4000) {
        this.init();
        
        const toast = document.createElement('div');
        
        // İkonlar
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️',
            sync: '🔄',
            firebase: '🔥',
            local: '💾'
        };
        
        // Renkler
        const colors = {
            success: { bg: '#dcfce7', border: '#22c55e', text: '#166534' },
            error: { bg: '#fee2e2', border: '#ef4444', text: '#991b1b' },
            warning: { bg: '#fef3c7', border: '#f59e0b', text: '#92400e' },
            info: { bg: '#dbeafe', border: '#3b82f6', text: '#1e40af' },
            sync: { bg: '#f3e8ff', border: '#a855f7', text: '#6b21a8' },
            firebase: { bg: '#ffedd5', border: '#f97316', text: '#9a3412' },
            local: { bg: '#e0e7ff', border: '#6366f1', text: '#3730a3' }
        };
        
        const color = colors[type] || colors.info;
        const icon = icons[type] || icons.info;
        
        toast.style.cssText = `
            display: flex;
            align-items: center;
            gap: 0.75rem;
            padding: 1rem 1.25rem;
            background: ${color.bg};
            border: 1px solid ${color.border};
            border-left: 4px solid ${color.border};
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            animation: slideInRight 0.3s ease;
            font-size: 0.9rem;
            color: ${color.text};
        `;
        
        toast.innerHTML = `
            <span style="font-size: 1.25rem;">${icon}</span>
            <span style="flex: 1; line-height: 1.4;">${message}</span>
            <button onclick="this.parentElement.remove()" style="
                background: none;
                border: none;
                font-size: 1.25rem;
                cursor: pointer;
                opacity: 0.5;
                color: inherit;
            ">×</button>
        `;
        
        this.container.appendChild(toast);
        
        // Otomatik kapat
        if (duration > 0) {
            setTimeout(() => {
                toast.style.animation = 'slideOutRight 0.3s ease forwards';
                setTimeout(() => toast.remove(), 300);
            }, duration);
        }
        
        return toast;
    },
    
    success(msg, duration) { return this.show(msg, 'success', duration); },
    error(msg, duration) { return this.show(msg, 'error', duration); },
    warning(msg, duration) { return this.show(msg, 'warning', duration); },
    info(msg, duration) { return this.show(msg, 'info', duration); },
    sync(msg, duration) { return this.show(msg, 'sync', duration); },
    firebase(msg, duration) { return this.show(msg, 'firebase', duration); },
    local(msg, duration) { return this.show(msg, 'local', duration); }
};

// Toast animasyonları için CSS ekle
const toastStyles = document.createElement('style');
toastStyles.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(toastStyles);

// Global erişim için
window.Toast = Toast;

// ==================== BAĞLANTI YÖNETİMİ ====================
let firebaseConnected = false;
let firebaseApp = null;
let firebaseDb = null;
let lastSyncTime = null;

// localStorage'dan force local modu oku
function getForceLocalMode() {
    return localStorage.getItem('emuhasebe_force_local') === 'true';
}

// Mod değiştirme
export function setMode(mode) {
    if (mode === 'local') {
        localStorage.setItem('emuhasebe_force_local', 'true');
        console.log('💾 LocalStorage moduna geçildi');
    } else if (mode === 'firebase') {
        localStorage.setItem('emuhasebe_force_local', 'false');
        console.log('🔥 Firebase moduna geçiliyor...');
    }
    // Mod değişikliği event'i
    window.dispatchEvent(new CustomEvent('db-mode-change', { detail: { mode } }));
}

// Mevcut modu al
export function getMode() {
    if (getForceLocalMode()) return 'local';
    return firebaseConnected ? 'firebase' : 'local';
}

// Firebase modüllerini dinamik import et
async function initFirebase() {
    // Manuel local mod aktifse Firebase'e bağlanma
    if (getForceLocalMode()) {
        console.log('💾 Manuel LocalStorage modu aktif');
        firebaseConnected = false;
        return false;
    }
    
    try {
        const { initializeApp } = await import('https://www.gstatic.com/firebasejs/11.0.0/firebase-app.js');
        const { getDatabase, ref, get, onValue } = await import('https://www.gstatic.com/firebasejs/11.0.0/firebase-database.js');
        const { firebaseConfig } = await import('./firebase-config.js');
        
        firebaseApp = initializeApp(firebaseConfig);
        firebaseDb = getDatabase(firebaseApp);
        
        // Bağlantı testi - basit bir okuma denemesi yap
        const testRef = ref(firebaseDb, 'connection_test');
        const testPromise = get(testRef);
        const timeoutPromise = new Promise((_, reject) =>
            setTimeout(() => reject(new Error('Firebase bağlantı zaman aşımı')), 1500)
        );
        
        await Promise.race([testPromise, timeoutPromise]);
        firebaseConnected = true;
        console.log('🔥 Firebase bağlantısı başarılı!');
        return true;
    } catch (error) {
        console.warn('⚠️ Firebase bağlantısı kurulamadı, localStorage kullanılacak:', error.message);
        firebaseConnected = false;
        return false;
    }
}

// Bağlantı durumunu al
export function isOnline() {
    return firebaseConnected && !getForceLocalMode();
}

// ==================== LOCALSTORAGE OPERASYONLARI ====================
const LocalDB = {
    // Veri al
    get: (collection) => {
        const data = localStorage.getItem(`emuhasebe_${collection}`);
        return data ? JSON.parse(data) : {};
    },
    
    // Veri kaydet
    set: (collection, data) => {
        localStorage.setItem(`emuhasebe_${collection}`, JSON.stringify(data));
        // Değişiklik event'i tetikle
        window.dispatchEvent(new CustomEvent('localdb-change', { detail: { collection } }));
    },
    
    // Benzersiz ID oluştur
    generateId: () => {
        return 'local_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
    }
};

// ==================== FIREBASE OPERASYONLARI ====================
let firebaseRefs = null;

async function getFirebaseRefs() {
    if (!firebaseRefs) {
        const { ref, push, set, get, update, remove, onValue } = 
            await import('https://www.gstatic.com/firebasejs/11.0.0/firebase-database.js');
        firebaseRefs = { ref, push, set, get, update, remove, onValue };
    }
    return firebaseRefs;
}

// ==================== GENERIC CRUD OPERASYONLARI ====================
function createCRUD(collectionName) {
    return {
        // Realtime dinle
        dinle: async (callback) => {
            if (firebaseConnected) {
                const { ref, onValue } = await getFirebaseRefs();
                const collectionRef = ref(firebaseDb, collectionName);
                onValue(collectionRef, (snapshot) => {
                    const data = snapshot.val();
                    const items = data ? Object.entries(data).map(([id, val]) => ({ id, ...val })) : [];
                    callback(items);
                });
            } else {
                // LocalStorage için polling veya event dinle
                const getData = () => {
                    const data = LocalDB.get(collectionName);
                    const items = Object.entries(data).map(([id, val]) => ({ id, ...val }));
                    callback(items);
                };
                getData(); // İlk yükleme
                
                // Değişiklik dinle
                window.addEventListener('localdb-change', (e) => {
                    if (e.detail.collection === collectionName) {
                        getData();
                    }
                });
            }
        },

        // Hepsini getir
        hepsiniGetir: async () => {
            if (firebaseConnected) {
                const { ref, get } = await getFirebaseRefs();
                const snapshot = await get(ref(firebaseDb, collectionName));
                const data = snapshot.val();
                return data ? Object.entries(data).map(([id, val]) => ({ id, ...val })) : [];
            } else {
                const data = LocalDB.get(collectionName);
                return Object.entries(data).map(([id, val]) => ({ id, ...val }));
            }
        },

        // Tek kayıt getir
        getir: async (id) => {
            if (firebaseConnected) {
                const { ref, get } = await getFirebaseRefs();
                const snapshot = await get(ref(firebaseDb, `${collectionName}/${id}`));
                return snapshot.val() ? { id, ...snapshot.val() } : null;
            } else {
                const data = LocalDB.get(collectionName);
                return data[id] ? { id, ...data[id] } : null;
            }
        },

        // Ekle
        ekle: async (item) => {
            const now = new Date().toISOString();
            const itemWithDates = {
                ...item,
                olusturma_tarihi: now,
                guncelleme_tarihi: now
            };

            if (firebaseConnected) {
                const { ref, push, set } = await getFirebaseRefs();
                const newRef = push(ref(firebaseDb, collectionName));
                await set(newRef, itemWithDates);
                return newRef.key;
            } else {
                const data = LocalDB.get(collectionName);
                const id = LocalDB.generateId();
                data[id] = itemWithDates;
                LocalDB.set(collectionName, data);
                return id;
            }
        },

        // Güncelle
        guncelle: async (id, item) => {
            const now = new Date().toISOString();
            
            if (firebaseConnected) {
                const { ref, update } = await getFirebaseRefs();
                await update(ref(firebaseDb, `${collectionName}/${id}`), {
                    ...item,
                    guncelleme_tarihi: now
                });
            } else {
                const data = LocalDB.get(collectionName);
                if (data[id]) {
                    data[id] = { ...data[id], ...item, guncelleme_tarihi: now };
                    LocalDB.set(collectionName, data);
                }
            }
        },

        // Sil
        sil: async (id) => {
            if (firebaseConnected) {
                const { ref, remove } = await getFirebaseRefs();
                await remove(ref(firebaseDb, `${collectionName}/${id}`));
            } else {
                const data = LocalDB.get(collectionName);
                delete data[id];
                LocalDB.set(collectionName, data);
            }
        }
    };
}

// ==================== MÜŞTERİLER ====================
export const Musteriler = {
    ...createCRUD('musteriler'),
    
    // Tip'e göre filtrele
    tipFiltrele: async (tip) => {
        const tumu = await Musteriler.hepsiniGetir();
        if (tip === 'hepsi') return tumu;
        return tumu.filter(m => m.tip === tip || m.tip === 'her_ikisi');
    }
};

// ==================== ÜRÜNLER ====================
export const Urunler = createCRUD('urunler');

// ==================== ALIŞ FATURALARI ====================
export const AlisFaturalari = {
    ...createCRUD('alis_faturalari'),
    
    // Bu ayki toplam
    aylikToplam: async () => {
        const faturalar = await AlisFaturalari.hepsiniGetir();
        const buAy = new Date();
        const ayBaslangic = new Date(buAy.getFullYear(), buAy.getMonth(), 1);
        
        return faturalar
            .filter(f => new Date(f.fatura_tarihi) >= ayBaslangic)
            .reduce((toplam, f) => toplam + (parseFloat(f.genel_toplam) || 0), 0);
    }
};

// ==================== SATIŞ FATURALARI ====================
export const SatisFaturalari = {
    ...createCRUD('satis_faturalari'),
    
    // Bu ayki toplam
    aylikToplam: async () => {
        const faturalar = await SatisFaturalari.hepsiniGetir();
        const buAy = new Date();
        const ayBaslangic = new Date(buAy.getFullYear(), buAy.getMonth(), 1);
        
        return faturalar
            .filter(f => new Date(f.fatura_tarihi) >= ayBaslangic)
            .reduce((toplam, f) => toplam + (parseFloat(f.genel_toplam) || 0), 0);
    }
};

// ==================== İADE FATURALARI ====================
export const IadeFaturalari = createCRUD('iade_faturalari');

// ==================== DASHBOARD İSTATİSTİKLERİ ====================
export const Dashboard = {
    // Tüm istatistikleri getir
    istatistikler: async () => {
        const [alis, satis, iade, musteriler, urunler] = await Promise.all([
            AlisFaturalari.hepsiniGetir(),
            SatisFaturalari.hepsiniGetir(),
            IadeFaturalari.hepsiniGetir(),
            Musteriler.hepsiniGetir(),
            Urunler.hepsiniGetir()
        ]);

        const buAy = new Date();
        const ayBaslangic = new Date(buAy.getFullYear(), buAy.getMonth(), 1);

        const aylikAlis = alis
            .filter(f => new Date(f.fatura_tarihi) >= ayBaslangic)
            .reduce((t, f) => t + (parseFloat(f.genel_toplam) || 0), 0);

        const aylikSatis = satis
            .filter(f => new Date(f.fatura_tarihi) >= ayBaslangic)
            .reduce((t, f) => t + (parseFloat(f.genel_toplam) || 0), 0);

        return {
            toplam_alis_fatura: alis.length,
            toplam_satis_fatura: satis.length,
            toplam_iade_fatura: iade.length,
            toplam_musteri: musteriler.length,
            toplam_urun: urunler.length,
            aylik_alis_toplam: aylikAlis,
            aylik_satis_toplam: aylikSatis,
            son_alis_faturalari: alis.sort((a, b) => new Date(b.olusturma_tarihi) - new Date(a.olusturma_tarihi)).slice(0, 5),
            son_satis_faturalari: satis.sort((a, b) => new Date(b.olusturma_tarihi) - new Date(a.olusturma_tarihi)).slice(0, 5)
        };
    },

    // Realtime dinleme
    dinle: async (callback) => {
        if (firebaseConnected) {
            const { ref, onValue } = await getFirebaseRefs();
            const collections = ['alis_faturalari', 'satis_faturalari', 'iade_faturalari', 'musteriler', 'urunler'];
            collections.forEach(col => {
                onValue(ref(firebaseDb, col), async () => {
                    const stats = await Dashboard.istatistikler();
                    callback(stats);
                });
            });
        } else {
            // İlk yükleme
            const stats = await Dashboard.istatistikler();
            callback(stats);
            
            // LocalDB değişikliklerini dinle
            window.addEventListener('localdb-change', async () => {
                const stats = await Dashboard.istatistikler();
                callback(stats);
            });
        }
    }
};

// ==================== YARDIMCI FONKSİYONLAR ====================
export const Yardimci = {
    // Para formatla
    paraFormat: (tutar) => {
        return new Intl.NumberFormat('tr-TR', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(tutar || 0);
    },

    // Tarih formatla
    tarihFormat: (tarih) => {
        if (!tarih) return '-';
        return new Date(tarih).toLocaleDateString('tr-TR');
    },

    // Benzersiz ID oluştur
    benzersizId: () => {
        return Date.now().toString(36) + Math.random().toString(36).substr(2);
    },
    
    // Fatura numarası oluştur
    faturaNo: (prefix = 'FTR') => {
        const tarih = new Date();
        const yil = tarih.getFullYear();
        const ay = String(tarih.getMonth() + 1).padStart(2, '0');
        const gun = String(tarih.getDate()).padStart(2, '0');
        const seri = String(Math.floor(Math.random() * 10000)).padStart(4, '0');
        return `${prefix}-${yil}${ay}${gun}-${seri}`;
    }
};

// ==================== SYNC (LocalStorage <-> Firebase) ====================
export const Sync = {
    collections: ['musteriler', 'urunler', 'alis_faturalari', 'satis_faturalari', 'iade_faturalari'],
    isSyncing: false,
    
    // Son senkronizasyon zamanını al
    getLastSyncTime() {
        return localStorage.getItem('emuhasebe_last_sync');
    },
    
    // Son senkronizasyon zamanını kaydet
    setLastSyncTime() {
        const now = new Date().toISOString();
        localStorage.setItem('emuhasebe_last_sync', now);
        lastSyncTime = now;
        return now;
    },
    
    // LocalStorage verilerini Firebase'e yükle
    uploadToFirebase: async (showToast = true) => {
        if (!firebaseConnected) {
            console.warn('Firebase bağlantısı yok, sync yapılamaz.');
            if (showToast) Toast.warning('Firebase bağlantısı yok, veriler yüklenemedi.');
            return false;
        }
        
        if (Sync.isSyncing) return false;
        Sync.isSyncing = true;
        
        try {
            const { ref, set, get } = await getFirebaseRefs();
            let uploadedCount = 0;
            
            for (const col of Sync.collections) {
                const localData = LocalDB.get(col);
                const localEntries = Object.entries(localData);
                
                if (localEntries.length > 0) {
                    // Firebase'deki mevcut verileri al
                    const snapshot = await get(ref(firebaseDb, col));
                    const firebaseData = snapshot.val() || {};
                    
                    // Local verileri Firebase'e yükle (merge)
                    for (const [localId, data] of localEntries) {
                        // Eğer Firebase'de bu ID yoksa veya local daha yeniyse yükle
                        if (!firebaseData[localId]) {
                            if (localId.startsWith('local_')) {
                                // Local ID'li kayıtları yeni Firebase ID ile yükle
                                const { push, set: setFn } = await getFirebaseRefs();
                                const newRef = push(ref(firebaseDb, col));
                                await setFn(newRef, { ...data, syncedAt: new Date().toISOString() });
                            } else {
                                // Normal ID'li kayıtları aynı ID ile yükle
                                await set(ref(firebaseDb, `${col}/${localId}`), { ...data, syncedAt: new Date().toISOString() });
                            }
                            uploadedCount++;
                        }
                    }
                }
            }
            
            Sync.setLastSyncTime();
            console.log(`✅ ${uploadedCount} kayıt Firebase'e yüklendi`);
            if (showToast && uploadedCount > 0) {
                Toast.sync(`${uploadedCount} kayıt Firebase'e yüklendi`);
            }
            return true;
        } catch (error) {
            console.error('Upload hatası:', error);
            if (showToast) Toast.error('Veriler yüklenirken hata oluştu!');
            return false;
        } finally {
            Sync.isSyncing = false;
        }
    },
    
    // Firebase verilerini LocalStorage'a indir
    downloadFromFirebase: async (showToast = true) => {
        if (!firebaseConnected) {
            console.warn('Firebase bağlantısı yok, download yapılamaz.');
            if (showToast) Toast.warning('Firebase bağlantısı yok, veriler indirilemedi.');
            return false;
        }
        
        if (Sync.isSyncing) return false;
        Sync.isSyncing = true;
        
        try {
            const { ref, get } = await getFirebaseRefs();
            let downloadedCount = 0;
            
            for (const col of Sync.collections) {
                const snapshot = await get(ref(firebaseDb, col));
                const firebaseData = snapshot.val() || {};
                const localData = LocalDB.get(col);
                
                // Firebase verilerini local'e merge et
                const mergedData = { ...localData };
                for (const [fbId, fbData] of Object.entries(firebaseData)) {
                    if (!mergedData[fbId]) {
                        mergedData[fbId] = fbData;
                        downloadedCount++;
                    }
                }
                
                LocalDB.set(col, mergedData);
            }
            
            Sync.setLastSyncTime();
            console.log(`✅ ${downloadedCount} kayıt LocalStorage'a indirildi`);
            if (showToast && downloadedCount > 0) {
                Toast.sync(`${downloadedCount} kayıt LocalStorage'a indirildi`);
            }
            return true;
        } catch (error) {
            console.error('Download hatası:', error);
            if (showToast) Toast.error('Veriler indirilirken hata oluştu!');
            return false;
        } finally {
            Sync.isSyncing = false;
        }
    },
    
    // İki yönlü tam senkronizasyon
    fullSync: async (showToast = true) => {
        if (!firebaseConnected) {
            if (showToast) Toast.warning('Firebase bağlantısı yok, senkronizasyon yapılamadı.');
            return false;
        }
        
        if (Sync.isSyncing) {
            if (showToast) Toast.info('Senkronizasyon zaten devam ediyor...');
            return false;
        }
        
        const syncToast = showToast ? Toast.sync('Veriler senkronize ediliyor...', 0) : null;
        
        try {
            // Önce Firebase'den indir
            await Sync.downloadFromFirebase(false);
            // Sonra local'i Firebase'e yükle
            await Sync.uploadToFirebase(false);
            
            Sync.setLastSyncTime();
            
            if (syncToast) syncToast.remove();
            if (showToast) Toast.success('Veriler başarıyla senkronize edildi! 🎉');
            console.log('🔄 Tam senkronizasyon tamamlandı');
            return true;
        } catch (error) {
            console.error('Sync hatası:', error);
            if (syncToast) syncToast.remove();
            if (showToast) Toast.error('Senkronizasyon sırasında hata oluştu!');
            return false;
        }
    },
    
    // Otomatik senkronizasyon başlat
    startAutoSync: (intervalMs = 60000) => {
        // Her dakika senkronize et
        setInterval(() => {
            if (firebaseConnected && !getForceLocalMode()) {
                Sync.fullSync(false).then(success => {
                    if (success) console.log('⏰ Otomatik senkronizasyon tamamlandı');
                });
            }
        }, intervalMs);
        console.log(`⏰ Otomatik senkronizasyon başlatıldı (${intervalMs/1000}sn)`);
    },
    
    // LocalStorage'ı temizle
    clearLocal: (showToast = true) => {
        Sync.collections.forEach(col => {
            localStorage.removeItem(`emuhasebe_${col}`);
        });
        console.log('🗑️ LocalStorage temizlendi');
        if (showToast) Toast.info('Yerel veriler temizlendi');
    }
};

// ==================== BAŞLATMA ====================
// NOT: initialized flag kaldırıldı - her sayfa yüklenmesinde mod kontrolü yapılır
let initPromise = null;

export async function init() {
    // Tek bir init işlemi garanti et
    if (initPromise) return initPromise;
    
    initPromise = (async () => {
        // Toast sistemini başlat
        Toast.init();
        
        // Her zaman güncel forceLocalMode durumunu oku
        await initFirebase();
        
        // Global erişim için window'a ekle
        window.DB = {
            isOnline,
            getMode,
            setMode,
            Musteriler,
            Urunler,
            AlisFaturalari,
            SatisFaturalari,
            IadeFaturalari,
            Dashboard,
            Yardimci,
            Sync,
            Toast
        };
        
        // Durum göster
        const mode = getMode();
        const forceLocal = getForceLocalMode();
        
        if (mode === 'firebase') {
            Toast.firebase('Firebase moduna bağlandı');
            
            // Firebase modunda otomatik senkronizasyon yap
            setTimeout(async () => {
                await Sync.fullSync(true);
                // Otomatik sync başlat (her 2 dakikada bir)
                Sync.startAutoSync(120000);
            }, 1000);
        } else {
            if (forceLocal) {
                Toast.local('LocalStorage modu aktif (Manuel)');
            } else {
                Toast.warning('Firebase bağlantısı kurulamadı, LocalStorage kullanılıyor');
            }
        }
        
        const status = mode === 'firebase' ? '🔥 Firebase' : '💾 LocalStorage';
        console.log(`${status} modu aktif${forceLocal ? ' (Manuel)' : ''}`);
        
        return firebaseConnected;
    })();
    
    return initPromise;
}

// Otomatik başlat
init();

// Default export
export default {
    init,
    isOnline,
    getMode,
    setMode,
    Musteriler,
    Urunler,
    AlisFaturalari,
    SatisFaturalari,
    IadeFaturalari,
    Dashboard,
    Yardimci,
    Sync
};
