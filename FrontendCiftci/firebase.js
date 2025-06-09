// Firebase modülleri - CDN'den import
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getDatabase, ref, push, set } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-database.js";
import { getAnalytics } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-analytics.js";

// Firebase yapılandırması
const firebaseConfig = {
    apiKey: "AIzaSyCHGIDWTdNFPs7FTfF__K5p6FAsBulawlo",
    authDomain: "ciftcitakipsistemi-abe8e.firebaseapp.com",
    databaseURL: "https://ciftcitakipsistemi-abe8e-default-rtdb.firebaseio.com",
    projectId: "ciftcitakipsistemi-abe8e",
    storageBucket: "ciftcitakipsistemi-abe8e.firebasestorage.app",
    messagingSenderId: "559590975377",
    appId: "1:559590975377:web:3b01663f973e258a089c30",
    measurementId: "G-SKX3FK88TZ"
};

// Firebase'i başlat
const app = initializeApp(firebaseConfig);
const db = getDatabase(app);
const analytics = getAnalytics(app);

// HTML elemanları
const form = document.getElementById("kayitForm");
const loading = document.getElementById("loading");
const successMsg = document.getElementById("successMsg");
const errorMsg = document.getElementById("errorMsg");

// Mesajları temizle
function clearMessages() {
    loading.style.display = 'none';
    successMsg.style.display = 'none';
    errorMsg.style.display = 'none';
}

// Başarı mesajı göster
function showSuccess() {
    clearMessages();
    successMsg.style.display = 'block';
    setTimeout(() => {
        successMsg.style.display = 'none';
    }, 3000);
}

// Hata mesajı göster
function showError(message = 'Kayıt sırasında hata oluştu.') {
    clearMessages();
    errorMsg.textContent = message;
    errorMsg.style.display = 'block';
}

// Loading göster
function showLoading() {
    clearMessages();
    loading.style.display = 'block';
}

// Test butonu ekleyelim
const testButton = document.createElement('button');
testButton.textContent = 'Test Veritabanı Bağlantısı';
testButton.style.cssText = 'margin: 10px; padding: 10px; background: #2196F3; color: white; border: none; border-radius: 5px; cursor: pointer;';
document.body.appendChild(testButton);

testButton.addEventListener('click', async () => {
    console.log('🧪 Test başlatılıyor...');
    try {
        const testRef = push(ref(db, "test"));
        await set(testRef, {
            mesaj: "Test verisi",
            zaman: new Date().toISOString(),
            tarayici: navigator.userAgent
        });
        console.log('✅ Test verisi başarıyla kaydedildi!');
        alert('✅ Test başarılı! Veritabanı çalışıyor.');
    } catch (error) {
        console.error('❌ Test hatası:', error);
        alert('❌ Test başarısız: ' + error.message);
    }
});

// Form gönderimi
form.addEventListener("submit", async (e) => {
    e.preventDefault();
    console.log('📝 Form gönderildi');

    // Form verilerini al ve validation yap
    const adSoyad = document.getElementById("adSoyad").value.trim();
    const sehir = document.getElementById("sehir").value.trim();
    const email = document.getElementById("email").value.trim();
    const sifre = document.getElementById("sifre").value;

    console.log('📋 Form verileri:', { adSoyad, sehir, email, sifre: '***' });

    // Validation kontrolü
    if (!adSoyad || !sehir || !email || !sifre) {
        console.log('❌ Validation hatası: Eksik alanlar');
        showError("Lütfen tüm alanları doldurun.");
        return;
    }

    if (sifre.length < 6) {
        console.log('❌ Validation hatası: Şifre çok kısa');
        showError("Şifre en az 6 karakter olmalı.");
        return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        console.log('❌ Validation hatası: Geçersiz email');
        showError("Geçerli bir e-posta adresi girin.");
        return;
    }

    console.log('✅ Validation başarılı');

    // Loading göster
    showLoading();

    try {
        console.log('💾 Veritabanına kaydetme başlatılıyor...');
        
        // Yeni kullanıcı referansı oluştur
        const yeniKullaniciRef = push(ref(db, "users"));
        console.log('🔗 Referans oluşturuldu:', yeniKullaniciRef.key);
        
        const userData = {
            adSoyad: adSoyad,
            sehir: sehir,
            email: email,
            sifre: btoa(sifre), // Basit encoding
            kayitTarihi: new Date().toISOString(),
            durum: "aktif",
            userId: yeniKullaniciRef.key
        };

        console.log('📦 Kaydedilecek veri:', userData);
        
        // Veriyi kaydet
        await set(yeniKullaniciRef, userData);

        console.log('✅ Kayıt başarılı! User ID:', yeniKullaniciRef.key);
        console.log('🔍 Firebase Console\'da kontrol edin: https://console.firebase.google.com/project/ciftcitakipsistemi-abe8e/database/ciftcitakipsistemi-abe8e-default-rtdb/data');
        showSuccess();
        form.reset();

    } catch (error) {
        console.error('❌ Kayıt hatası:', error);
        console.error('Hata kodu:', error.code);
        console.error('Hata mesajı:', error.message);
        
        // Hata türüne göre mesaj göster
        if (error.code === 'PERMISSION_DENIED') {
            showError("Veritabanına erişim izni yok. Database kurallarını kontrol edin.");
        } else if (error.code === 'NETWORK_ERROR') {
            showError("İnternet bağlantınızı kontrol edin.");
        } else {
            showError("Kayıt sırasında hata oluştu: " + error.message);
        }
    }
});

// Sayfa yüklendiğinde Firebase bağlantısını test et
window.addEventListener('load', () => {
    console.log('🔥 Firebase Realtime Database başlatıldı');
    console.log('📡 Database URL:', firebaseConfig.databaseURL);
    console.log('🔑 Project ID:', firebaseConfig.projectId);
    console.log('📊 Analytics aktif');
    
    // Bağlantı durumunu göster
    console.log('🌐 Firebase Console Link: https://console.firebase.google.com/project/ciftcitakipsistemi-abe8e/database/ciftcitakipsistemi-abe8e-default-rtdb/data');
});