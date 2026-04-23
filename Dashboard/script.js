const API_URL = "/api/weather"; 

// --- BIẾN TOÀN CỤC ---
let latestWeatherData = {}; // Lưu trữ dữ liệu mới nhất
let isCelsius = true;       // Trạng thái đơn vị nhiệt độ (mặc định là độ C)

// --- CHỨC NĂNG 1: HIỂN THỊ VÀ CẬP NHẬT DỮ LIỆU ---
function updateStationData(stationId, data) {
    // Tính toán nhiệt độ theo đơn vị đang chọn
    let displayTemp = data.temperature;
    if (!isCelsius) {
        displayTemp = (displayTemp * 1.8) + 32; // Công thức đổi độ C sang độ F
    }

    // 1. Cập nhật nhiệt độ
    document.getElementById(`${stationId}-temp`).textContent = displayTemp.toFixed(1);
    
    // Cập nhật chữ °C hay °F
    const tempUnitElements = document.querySelectorAll(`#card-${stationId} .celsius`);
    const toggleUnitElements = document.querySelectorAll(`#card-${stationId} .unit-toggle`);
    
    tempUnitElements.forEach(el => el.textContent = isCelsius ? "°C" : "°F");
    toggleUnitElements.forEach(el => el.textContent = isCelsius ? "°C" : "°F");
    
    // 2. Cập nhật độ ẩm
    document.getElementById(`${stationId}-hum`).textContent = data.humidity.toFixed(1) + "%";
    
    // 3. Cập nhật trạng thái mưa & Icon
    const rainElement = document.getElementById(`${stationId}-rain`);
    const iconElement = document.getElementById(`${stationId}-icon`);

    if (data.isRaining) {
        rainElement.textContent = "Có mưa";
        rainElement.className = "detail-value status rain";
        iconElement.className = "fa-solid fa-cloud-showers-heavy weather-icon rainy";
    } else {
        rainElement.textContent = "Không mưa";
        rainElement.className = "detail-value status clear";
        iconElement.className = "fa-solid fa-cloud-sun weather-icon";
    }
}

// Hàm kết nối Server lấy dữ liệu
async function fetchData() {
    try {
        const response = await fetch(API_URL);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        latestWeatherData = await response.json(); // Lưu vào biến toàn cục
        
        // Gọi hàm update cho từng trạm
        if (latestWeatherData.hanoi) updateStationData('hanoi', latestWeatherData.hanoi);
        if (latestWeatherData.danang) updateStationData('danang', latestWeatherData.danang);
        if (latestWeatherData.tphcm) updateStationData('tphcm', latestWeatherData.tphcm);

    } catch (error) {
        console.error("Lỗi khi tải dữ liệu từ API:", error);
    }
}

// --- CHỨC NĂNG 2: ĐỔI ĐƠN VỊ NHIỆT ĐỘ (°C <-> °F) ---
function setupUnitToggle() {
    const unitToggles = document.querySelectorAll('.unit-toggle');
    unitToggles.forEach(toggle => {
        toggle.addEventListener('click', () => {
            isCelsius = !isCelsius; // Đảo ngược trạng thái
            
            // Render lại giao diện ngay lập tức với dữ liệu mới nhất
            if (latestWeatherData.hanoi) updateStationData('hanoi', latestWeatherData.hanoi);
            if (latestWeatherData.danang) updateStationData('danang', latestWeatherData.danang);
            if (latestWeatherData.tphcm) updateStationData('tphcm', latestWeatherData.tphcm);
        });
    });
}

// --- CHỨC NĂNG 3: TÌM KIẾM TRẠM THỜI TIẾT ---
function setupSearch() {
    const searchInput = document.getElementById('search-input');
    const allCards = document.querySelectorAll('.weather-card');

    if(searchInput) {
        searchInput.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase().trim();

            allCards.forEach(card => {
                const locationName = card.querySelector('.location').innerText.toLowerCase();
                
                // Nếu tên địa điểm có chứa từ khóa gõ vào -> hiện, ngược lại -> ẩn
                if (locationName.includes(searchTerm)) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
}

// --- CHỨC NĂNG 4: HIỆU ỨNG MENU SIDEBAR ---
function setupSidebar() {
    const menuIcons = document.querySelectorAll('.menu-icon');
    
    menuIcons.forEach(icon => {
        icon.addEventListener('click', () => {
            // Xóa class 'active' ở tất cả các icon
            menuIcons.forEach(i => i.classList.remove('active'));
            // Thêm class 'active' vào icon vừa click
            icon.classList.add('active');
        });
    });
}

// --- KHỞI CHẠY TẤT CẢ KHI WEB VỪA LOAD ---
document.addEventListener('DOMContentLoaded', () => {
    // 1. Khởi tạo các chức năng phụ
    setupUnitToggle();
    setupSearch();
    setupSidebar();

    // 2. Lấy dữ liệu lần đầu
    fetchData();
    
    // 3. Tự động lấy dữ liệu liên tục mỗi 2 giây
    setInterval(fetchData, 2000);
});