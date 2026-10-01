<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 책 저장소 & 캘린더</title>

    <!-- Google Fonts: Gowun Dodum & Noto Sans KR -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Gamja+Flower&family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">

    <!-- Tailwind CSS CDN -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    fontFamily: {
                        gowun: ['"Gowun Dodum"', 'sans-serif'],
                        gamja: ['"Gamja Flower"', 'cursive'],
                        sans: ['"Noto Sans KR"', '"Gowun Dodum"', 'sans-serif'],
                    },
                    colors: {
                        pastel: {
                            pink: '#fce7f3',
                            pinkDark: '#f472b6',
                            purple: '#f3e8ff',
                            purpleDark: '#c084fc',
                            violet: '#a855f7',
                        }
                    }
                }
            }
        }
    </script>

    <!-- Canvas Confetti Library -->
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>

    <!-- Phosphor Icons -->
    <script src="https://unpkg.com/@phosphor-icons/web"></script>

    <style>
        body {
            font-family: 'Gowun Dodum', 'Noto Sans KR', sans-serif;
            background: linear-gradient(135deg, #fdf2f8 0%, #f3e8ff 50%, #eef2ff 100%);
            background-attachment: fixed;
            color: #374151;
        }

        /* 깔끔하고 얇은 캘린더 그리드 선 스타일링 */
        .calendar-grid {
            display: grid;
            grid-template-columns: repeat(7, minmax(0, 1fr));
            border-top: 1px solid #f3e8ff;
            border-left: 1px solid #f3e8ff;
        }

        .calendar-day-cell {
            border-right: 1px solid #f1f5f9;
            border-bottom: 1px solid #f1f5f9;
            min-height: 100px;
            background-color: rgba(255, 255, 255, 0.75);
            transition: all 0.2s ease;
        }

        .calendar-day-cell:hover {
            background-color: rgba(252, 231, 243, 0.4);
        }

        .calendar-header-cell {
            border-right: 1px solid #f3e8ff;
            border-bottom: 1px solid #e9d5ff;
            background-color: rgba(243, 232, 255, 0.5);
        }

        /* Custom Scrollbar */
        ::-webkit-scrollbar {
            width: 6px;
            height: 6px;
        }
        ::-webkit-scrollbar-track {
            background: #fbcfe8;
        }
        ::-webkit-scrollbar-thumb {
            background: #f472b6;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: #e879f9;
        }
    </style>
</head>
<body class="min-h-screen flex flex-col md:flex-row text-slate-700">

    <!-- Sidebar -->
    <aside class="w-full md:w-80 bg-white/70 backdrop-blur-md border-r border-purple-100/80 p-5 flex flex-col gap-6 shrink-0 shadow-sm">
        <div class="flex items-center gap-3 border-b border-pink-100 pb-4">
            <div class="w-10 h-10 rounded-2xl bg-gradient-to-tr from-pink-400 to-purple-400 flex items-center justify-center text-white text-xl shadow-md shadow-pink-200">
                📚
            </div>
            <div>
                <h1 class="text-xl font-bold bg-gradient-to-r from-pink-600 to-purple-600 bg-clip-text text-transparent tracking-tight">책 저장소 & 캘린더</h1>
                <p class="text-xs text-purple-400">파스텔 독서 일기장</p>
            </div>
        </div>

        <!-- Add Book Form Section -->
        <div class="space-y-4">
            <h2 class="text-sm font-bold flex items-center gap-2 text-slate-700">
                <i class="ph-bold ph-plus-circle text-pink-500"></i> 새 책 등록하기
            </h2>

            <!-- Search Field -->
            <div class="space-y-1">
                <label class="text-xs font-medium text-slate-500">책 제목 검색</label>
                <div class="flex gap-1.5">
                    <input type="text" id="searchInput" placeholder="예: 어린 왕자, 아몬드..." 
                        class="w-full text-xs p-2.5 rounded-xl border border-pink-100 focus:outline-none focus:ring-2 focus:ring-pink-300 bg-white/90 shadow-sm transition-all">
                    <button onclick="searchBooks()" 
                        class="bg-gradient-to-r from-pink-400 to-purple-400 hover:from-pink-500 hover:to-purple-500 text-white p-2.5 rounded-xl transition-all shadow-sm flex items-center justify-center">
                        <i class="ph-bold ph-magnifying-glass text-base"></i>
                    </button>
                </div>
            </div>

            <!-- Search Results Dropdown -->
            <div id="searchResultsContainer" class="hidden space-y-1">
                <label class="text-xs font-medium text-slate-500">검색 결과 선택</label>
                <select id="searchResultsSelect" onchange="onSelectSearchResult()" 
                    class="w-full text-xs p-2.5 rounded-xl border border-purple-100 focus:outline-none focus:ring-2 focus:ring-purple-300 bg-white/90">
                </select>
            </div>

            <!-- Selected Book Metadata Form -->
            <div class="space-y-3 pt-2 border-t border-purple-100/60">
                <div>
                    <label class="text-xs font-medium text-slate-500">선택된 도서</label>
                    <div id="selectedBookTitle" class="text-xs font-semibold text-slate-700 p-2.5 bg-purple-50/50 rounded-xl border border-purple-100/80 truncate">
                        검색 후 책을 선택해 주세요
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-2">
                    <div>
                        <label class="text-xs font-medium text-slate-500">전체 페이지 수</label>
                        <input type="number" id="inputTotalPages" min="1" value="300" 
                            class="w-full text-xs p-2.5 rounded-xl border border-purple-100 focus:outline-none focus:ring-2 focus:ring-purple-300 bg-white/90">
                    </div>
                    <div>
                        <label class="text-xs font-medium text-slate-500">목표 독서 상태</label>
                        <select id="inputStatus" 
                            class="w-full text-xs p-2.5 rounded-xl border border-purple-100 focus:outline-none focus:ring-2 focus:ring-purple-300 bg-white/90">
                            <option value="읽는 중">읽는 중</option>
                            <option value="읽기 완료">읽기 완료</option>
                            <option value="읽고 싶음">읽고 싶음</option>
                        </select>
                    </div>
                </div>

                <div>
                    <label class="text-xs font-medium text-slate-500">목표 완독일</label>
                    <input type="date" id="inputTargetDate" 
                        class="w-full text-xs p-2.5 rounded-xl border border-purple-100 focus:outline-none focus:ring-2 focus:ring-purple-300 bg-white/90">
                </div>

                <button onclick="addBookToShelf()" 
                    class="w-full bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 hover:opacity-95 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shadow-pink-200 transition-all flex items-center justify-center gap-2 text-xs">
                    <i class="ph-bold ph-book-bookmark text-base"></i> 내 책장에 추가
                </button>
            </div>
        </div>

        <!-- Info Card -->
        <div class="mt-auto bg-gradient-to-br from-pink-50 to-purple-50 p-3.5 rounded-2xl border border-purple-100/80 text-xs text-purple-600 space-y-1">
            <p class="font-bold flex items-center gap-1.5"><i class="ph-bold ph-sparkle"></i> 파스텔 테마 적용</p>
            <p class="text-[11px] text-purple-400 leading-relaxed">깔끔한 라인의 파스텔 캘린더에서 완독 예정일을 한눈에 확인해보세요.</p>
        </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col min-w-0">
        <!-- Top Navbar Header -->
        <header class="bg-white/60 backdrop-blur-md border-b border-purple-100/80 px-6 py-4 flex flex-wrap items-center justify-between gap-4">
            <div>
                <h2 class="text-xl font-bold bg-gradient-to-r from-pink-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">독서 일기 & 파스텔 캘린더</h2>
                <p class="text-xs text-slate-400">깔끔한 그리드 선과 파스텔 톤으로 정리하는 나만의 독서 스케줄</p>
            </div>
            
            <!-- Quick Stats -->
            <div class="flex gap-2.5 text-xs font-medium">
                <div class="bg-pink-100/70 text-pink-700 px-3 py-1.5 rounded-full border border-pink-200/50 flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-pink-400"></span>
                    <span>읽는 중:</span> <span id="statReading" class="font-bold">0</span>권
                </div>
                <div class="bg-purple-100/70 text-purple-700 px-3 py-1.5 rounded-full border border-purple-200/50 flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-purple-400"></span>
                    <span>완독:</span> <span id="statCompleted" class="font-bold">0</span>권
                </div>
                <div class="bg-indigo-100/70 text-indigo-700 px-3 py-1.5 rounded-full border border-indigo-200/50 flex items-center gap-1.5">
                    <span class="w-2 h-2 rounded-full bg-indigo-400"></span>
                    <span>위시:</span> <span id="statWishlist" class="font-bold">0</span>권
                </div>
            </div>
        </header>

        <!-- Navigation Tabs -->
        <div class="bg-white/40 backdrop-blur-sm border-b border-purple-100/60 px-6 flex gap-1 overflow-x-auto">
            <button onclick="switchTab('calendar')" id="tabBtn-calendar" 
                class="tab-btn px-4 py-3 font-semibold text-xs border-b-2 border-pink-500 text-pink-600 flex items-center gap-2 transition-all">
                📅 파스텔 캘린더
            </button>
            <button onclick="switchTab('reading')" id="tabBtn-reading" 
                class="tab-btn px-4 py-3 font-medium text-xs border-b-2 border-transparent text-slate-500 hover:text-purple-600 flex items-center gap-2 transition-all">
                📖 읽는 중
            </button>
            <button onclick="switchTab('completed')" id="tabBtn-completed" 
                class="tab-btn px-4 py-3 font-medium text-xs border-b-2 border-transparent text-slate-500 hover:text-purple-600 flex items-center gap-2 transition-all">
                ✅ 읽기 완료
            </button>
            <button onclick="switchTab('wishlist')" id="tabBtn-wishlist" 
                class="tab-btn px-4 py-3 font-medium text-xs border-b-2 border-transparent text-slate-500 hover:text-purple-600 flex items-center gap-2 transition-all">
                📌 읽고 싶음
            </button>
            <button onclick="switchTab('python')" id="tabBtn-python" 
                class="tab-btn ml-auto px-4 py-3 font-medium text-xs border-b-2 border-transparent text-purple-500 hover:text-purple-700 flex items-center gap-2 transition-all">
                🐍 Python main.py
            </button>
        </div>

        <!-- Content Views Section -->
        <div class="p-6 flex-1 overflow-y-auto">
            <!-- CALENDAR VIEW SECTION -->
            <div id="calendarView" class="space-y-4">
                <!-- Calendar Header / Controls -->
                <div class="bg-white/80 backdrop-blur-md p-4 rounded-2xl border border-purple-100/80 shadow-sm flex items-center justify-between">
                    <div class="flex items-center gap-3">
                        <button onclick="changeMonth(-1)" class="w-8 h-8 rounded-xl bg-purple-50 hover:bg-purple-100 text-purple-600 flex items-center justify-center border border-purple-200/50 transition-colors">
                            <i class="ph-bold ph-caret-left"></i>
                        </button>
                        <h3 id="calendarMonthYear" class="text-base font-bold text-slate-700">2026년 10월</h3>
                        <button onclick="changeMonth(1)" class="w-8 h-8 rounded-xl bg-purple-50 hover:bg-purple-100 text-purple-600 flex items-center justify-center border border-purple-200/50 transition-colors">
                            <i class="ph-bold ph-caret-right"></i>
                        </button>
                    </div>

                    <div class="flex items-center gap-3 text-xs font-medium">
                        <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-pink-400"></span> 목표 완독일</span>
                        <span class="flex items-center gap-1"><span class="w-2.5 h-2.5 rounded-full bg-purple-400"></span> 오늘</span>
                    </div>
                </div>

                <!-- Clean Styled Pastel Calendar Grid Container -->
                <div class="bg-white/90 backdrop-blur-md rounded-2xl border border-purple-100 shadow-sm overflow-hidden p-1">
                    <!-- Weekday Header -->
                    <div class="grid grid-cols-7 text-center font-semibold text-xs py-2.5 text-purple-500 bg-purple-50/40 rounded-t-xl border-b border-purple-100">
                        <div class="text-pink-500">일</div>
                        <div>월</div>
                        <div>화</div>
                        <div>수</div>
                        <div>목</div>
                        <div>금</div>
                        <div class="text-indigo-400">토</div>
                    </div>

                    <!-- Day Grid -->
                    <div id="calendarGrid" class="grid grid-cols-7 divide-x divide-y divide-purple-50/80 rounded-b-xl overflow-hidden bg-white/60">
                        <!-- Days generated via JavaScript -->
                    </div>
                </div>
            </div>

            <!-- Books Shelf Container -->
            <div id="booksGrid" class="hidden grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <!-- Book Cards will be rendered dynamically here -->
            </div>

            <!-- Empty State Display -->
            <div id="emptyState" class="hidden flex flex-col items-center justify-center py-16 text-center space-y-3">
                <div class="w-16 h-16 rounded-full bg-purple-100/60 flex items-center justify-center text-purple-400 text-3xl">
                    <i class="ph-duotone ph-books"></i>
                </div>
                <p class="text-slate-400 font-medium text-xs">등록된 책이 없습니다.<br>좌측 사이드바에서 새 책을 저장소에 추가해보세요!</p>
            </div>

            <!-- Python Streamlit Code Display View -->
            <div id="pythonCodeView" class="hidden space-y-4">
                <div class="flex items-center justify-between bg-white/80 backdrop-blur-md p-4 rounded-2xl border border-purple-100 shadow-sm">
                    <div>
                        <h3 class="font-bold text-slate-700 text-sm flex items-center gap-2">
                            <i class="ph-bold ph-code text-purple-500"></i> Streamlit 전용 main.py 코드
                        </h3>
                        <p class="text-xs text-slate-400">고운돋움 폰트 스타일이 적용된 최신 main.py 소스코드입니다.</p>
                    </div>
                    <button onclick="copyPythonCode()" 
                        class="bg-gradient-to-r from-purple-500 to-indigo-500 hover:opacity-90 text-white font-semibold text-xs py-2 px-3 rounded-xl shadow-sm transition-all flex items-center gap-1">
                        <i class="ph-bold ph-copy"></i> 코드 복사
                    </button>
                </div>

                <pre class="bg-slate-900 text-purple-200 p-4 rounded-2xl text-xs overflow-x-auto font-mono leading-relaxed shadow-inner"><code id="pythonCodeBlock">
import streamlit as st
import pandas as pd
import datetime
import requests

# -----------------------------------------------------------------------------
# 1. 페이지 기본 설정 및 세션 상태 초기화
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="책 저장소 & 파스텔 캘린더",
    page_icon="📚",
    layout="wide"
)

# 고운돋움 폰트 및 파스텔 그래디언트 테마 적용
st.markdown("""
    &lt;style&gt;
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&display=swap');

    html, body, [class*="css"], div, span, label, input, button {
        font-family: 'Gowun Dodum', sans-serif !important;
    }
    
    .stApp {
        background: linear-gradient(135deg, #fdf2f8 0%, #f3e8ff 50%, #eef2ff 100%);
    }
    &lt;/style&gt;
""", unsafe_allow_html=True)

if "my_books" not in st.session_state:
    st.session_state.my_books = []

# -----------------------------------------------------------------------------
# 2. 메인 화면 및 탭
# -----------------------------------------------------------------------------
st.title("📚 파스텔 독서 저장소")
st.caption("깔끔한 캘린더와 목표일 계산기로 즐겁게 독서하세요.")
</code></pre>
            </div>
        </div>
    </main>

    <script>
        // Sample Books Data with Dates
        let books = [
            {
                id: 1,
                title: "불편한 편의점",
                author: "김호연",
                cover_url: "https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=350&auto=format&fit=crop",
                total_pages: 268,
                current_page: 120,
                target_date: getFutureDateStr(5),
                status: "읽는 중"
            },
            {
                id: 2,
                title: "달러구트 꿈 백화점",
                author: "이미예",
                cover_url: "https://images.unsplash.com/photo-1512820790803-83ca734da794?q=80&w=350&auto=format&fit=crop",
                total_pages: 300,
                current_page: 300,
                target_date: getFutureDateStr(-2),
                status: "읽기 완료"
            },
            {
                id: 3,
                title: "세이노의 가르침",
                author: "세이노",
                cover_url: "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?q=80&w=350&auto=format&fit=crop",
                total_pages: 700,
                current_page: 0,
                target_date: getFutureDateStr(18),
                status: "읽고 싶음"
            }
        ];

        let currentTab = 'calendar';
        let currentCalendarDate = new Date(); // default current month/year
        let searchResults = [];
        let selectedSearchResult = null;

        window.addEventListener('DOMContentLoaded', () => {
            document.getElementById('inputTargetDate').value = getFutureDateStr(14);
            updateStats();
            renderCalendar();
            renderBooks();
        });

        function getFutureDateStr(days) {
            const date = new Date();
            date.setDate(date.getDate() + days);
            return date.toISOString().split('T')[0];
        }

        // Calendar Logic with Clean Grid Lines
        function changeMonth(offset) {
            currentCalendarDate.setMonth(currentCalendarDate.getMonth() + offset);
            renderCalendar();
        }

        function renderCalendar() {
            const year = currentCalendarDate.getFullYear();
            const month = currentCalendarDate.getMonth();

            const monthNames = ["1월", "2월", "3월", "4월", "5월", "6월", "7월", "8월", "9월", "10월", "11월", "12월"];
            document.getElementById('calendarMonthYear').textContent = `${year}년 ${monthNames[month]}`;

            const calendarGrid = document.getElementById('calendarGrid');
            calendarGrid.innerHTML = '';

            const firstDay = new Date(year, month, 1).getDay();
            const lastDate = new Date(year, month + 1, 0).getDate();
            const prevLastDate = new Date(year, month, 0).getDate();

            const today = new Date();
            const isCurrentMonth = today.getFullYear() === year && today.getMonth() === month;
            const todayDateNum = today.getDate();

            // Previous month padding days
            for (let i = firstDay - 1; i >= 0; i--) {
                const dayNum = prevLastDate - i;
                const cell = document.createElement('div');
                cell.className = "p-2 min-h-[90px] bg-slate-50/30 text-slate-300 text-xs font-light";
                cell.innerHTML = `<span class="opacity-40">${dayNum}</span>`;
                calendarGrid.appendChild(cell);
            }

            // Current month days
            for (let day = 1; day <= lastDate; day++) {
                const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                const isToday = isCurrentMonth && day === todayDateNum;

                const dayBooks = books.filter(b => b.target_date === dateStr);

                const cell = document.createElement('div');
                cell.className = `p-2 min-h-[95px] transition-colors relative ${isToday ? 'bg-purple-50/80 font-semibold' : 'hover:bg-pink-50/30'}`;

                let badgesHtml = '';
                dayBooks.forEach(b => {
                    const statusColor = b.status === '읽는 중' ? 'bg-pink-100 text-pink-700 border-pink-200' :
                                       b.status === '읽기 완료' ? 'bg-purple-100 text-purple-700 border-purple-200' :
                                       'bg-indigo-100 text-indigo-700 border-indigo-200';

                    badgesHtml += `
                        <div class="mt-1 text-[10px] p-1 px-1.5 rounded-lg border ${statusColor} truncate shadow-2xs font-medium flex items-center gap-1" title="${b.title}">
                            <span class="w-1.5 h-1.5 rounded-full bg-current shrink-0"></span>
                            <span class="truncate">${b.title}</span>
                        </div>
                    `;
                });

                cell.innerHTML = `
                    <div class="flex items-center justify-between">
                        <span class="text-xs ${isToday ? 'w-5 h-5 rounded-full bg-purple-500 text-white flex items-center justify-center font-bold shadow-xs' : 'text-slate-600'}">${day}</span>
                        ${dayBooks.length > 0 ? `<span class="text-[10px] text-pink-500 font-bold">📖 ${dayBooks.length}</span>` : ''}
                    </div>
                    <div class="space-y-0.5 mt-1">
                        ${badgesHtml}
                    </div>
                `;

                calendarGrid.appendChild(cell);
            }

            // Next month padding days to complete 35 or 42 grid cells
            const totalCellsSoFar = firstDay + lastDate;
            const remainingCells = (totalCellsSoFar % 7 === 0) ? 0 : 7 - (totalCellsSoFar % 7);

            for (let i = 1; i <= remainingCells; i++) {
                const cell = document.createElement('div');
                cell.className = "p-2 min-h-[90px] bg-slate-50/30 text-slate-300 text-xs font-light";
                cell.innerHTML = `<span class="opacity-40">${i}</span>`;
                calendarGrid.appendChild(cell);
            }
        }

        // Search Books Logic
        async function searchBooks() {
            const query = document.getElementById('searchInput').value.trim();
            if (!query) return;

            const resultsContainer = document.getElementById('searchResultsContainer');
            const resultsSelect = document.getElementById('searchResultsSelect');
            resultsSelect.innerHTML = '<option value="">검색 중...</option>';
            resultsContainer.classList.remove('hidden');

            try {
                const response = await fetch(`https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(query)}&maxResults=5`);
                const data = await response.json();

                if (data.items && data.items.length > 0) {
                    searchResults = data.items.map(item => {
                        const info = item.volumeInfo;
                        let thumbnail = info.imageLinks?.thumbnail || info.imageLinks?.smallThumbnail;
                        if (thumbnail) {
                            thumbnail = thumbnail.replace('http:', 'https:');
                        } else {
                            thumbnail = 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=350&auto=format&fit=crop';
                        }
                        return {
                            title: info.title || query,
                            author: info.authors ? info.authors.join(', ') : '저자 미상',
                            cover_url: thumbnail,
                            pageCount: info.pageCount || 300
                        };
                    });
                } else {
                    fallbackSearch(query);
                }
            } catch (err) {
                fallbackSearch(query);
            }

            resultsSelect.innerHTML = '';
            searchResults.forEach((book, index) => {
                const option = document.createElement('option');
                option.value = index;
                option.textContent = `${book.title} (${book.author})`;
                resultsSelect.appendChild(option);
            });

            if (searchResults.length > 0) {
                resultsSelect.selectedIndex = 0;
                onSelectSearchResult();
            }
        }

        function fallbackSearch(query) {
            searchResults = [{
                title: query,
                author: "추천 저자",
                cover_url: "https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=350&auto=format&fit=crop",
                pageCount: 300
            }];
        }

        function onSelectSearchResult() {
            const select = document.getElementById('searchResultsSelect');
            const idx = select.value;
            if (idx !== "") {
                selectedSearchResult = searchResults[idx];
                document.getElementById('selectedBookTitle').textContent = selectedSearchResult.title;
                if (selectedSearchResult.pageCount) {
                    document.getElementById('inputTotalPages').value = selectedSearchResult.pageCount;
                }
            }
        }

        function addBookToShelf() {
            const title = selectedSearchResult ? selectedSearchResult.title : document.getElementById('searchInput').value.trim();
            if (!title) {
                alert('책 제목을 입력하거나 검색해 주세요!');
                return;
            }

            const author = selectedSearchResult ? selectedSearchResult.author : "저자 미상";
            const cover_url = selectedSearchResult ? selectedSearchResult.cover_url : "https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=350&auto=format&fit=crop";
            const total_pages = parseInt(document.getElementById('inputTotalPages').value) || 300;
            const status = document.getElementById('inputStatus').value;
            const target_date = document.getElementById('inputTargetDate').value || getFutureDateStr(14);

            const newBook = {
                id: Date.now(),
                title: title,
                author: author,
                cover_url: cover_url,
                total_pages: total_pages,
                current_page: 0,
                target_date: target_date,
                status: status
            };

            books.push(newBook);
            updateStats();
            renderCalendar();
            renderBooks();

            document.getElementById('searchInput').value = '';
            document.getElementById('searchResultsContainer').classList.add('hidden');
            document.getElementById('selectedBookTitle').textContent = '검색 후 책을 선택해 주세요';
            selectedSearchResult = null;

            alert(`'${title}' 책이 성공적으로 저장소 및 캘린더에 추가되었습니다!`);
        }

        function calculateDailyTarget(book) {
            const today = new Date();
            today.setHours(0,0,0,0);

            const targetDate = new Date(book.target_date);
            targetDate.setHours(0,0,0,0);

            const timeDiff = targetDate.getTime() - today.getTime();
            const remainingDays = Math.ceil(timeDiff / (1000 * 3600 * 24));
            const remainingPages = book.total_pages - book.current_page;

            if (remainingPages <= 0) {
                return { dailyTarget: 0, remainingDays: 0, message: "완독 완료!" };
            }

            if (remainingDays <= 0) {
                return { dailyTarget: remainingPages, remainingDays: 0, message: "오늘이 목표일입니다!" };
            }

            const dailyTarget = Math.ceil(remainingPages / remainingDays);
            return { dailyTarget, remainingDays, message: null };
        }

        function renderBooks() {
            const grid = document.getElementById('booksGrid');
            const emptyState = document.getElementById('emptyState');
            const pythonView = document.getElementById('pythonCodeView');
            const calendarView = document.getElementById('calendarView');

            if (currentTab === 'calendar') {
                calendarView.classList.remove('hidden');
                grid.classList.add('hidden');
                emptyState.classList.add('hidden');
                pythonView.classList.add('hidden');
                return;
            } else {
                calendarView.classList.add('hidden');
            }

            if (currentTab === 'python') {
                grid.classList.add('hidden');
                emptyState.classList.add('hidden');
                pythonView.classList.remove('hidden');
                return;
            } else {
                pythonView.classList.add('hidden');
            }

            const statusMap = {
                'reading': '읽는 중',
                'completed': '읽기 완료',
                'wishlist': '읽고 싶음'
            };

            const targetStatus = statusMap[currentTab];
            const filteredBooks = books.filter(b => b.status === targetStatus);

            if (filteredBooks.length === 0) {
                grid.innerHTML = '';
                grid.classList.add('hidden');
                emptyState.classList.remove('hidden');
                return;
            } else {
                grid.classList.remove('hidden');
                emptyState.classList.add('hidden');
            }

            grid.innerHTML = filteredBooks.map(book => {
                const progressPct = Math.min(Math.round((book.current_page / book.total_pages) * 100), 100);
                const calc = calculateDailyTarget(book);

                return `
                    <div class="bg-white/80 backdrop-blur-md rounded-2xl overflow-hidden border border-purple-100/80 shadow-sm hover:shadow-md transition-all flex flex-col">
                        <div class="bg-purple-50/50 p-4 flex justify-center items-center border-b border-purple-100/60 relative">
                            <img src="${book.cover_url}" alt="${book.title}" 
                                class="h-40 object-cover rounded-xl shadow-md border border-purple-100"
                                onerror="this.src='https://images.unsplash.com/photo-1544947950-fa07a98d237f?q=80&w=350&auto=format&fit=crop'">
                            <span class="absolute top-2.5 right-2.5 text-[10px] bg-white/90 backdrop-blur-sm text-pink-600 px-2 py-0.5 rounded-full font-bold border border-pink-100 shadow-2xs">
                                ${book.status}
                            </span>
                        </div>

                        <div class="p-4 flex-1 flex flex-col justify-between space-y-3">
                            <div>
                                <h3 class="font-bold text-sm text-slate-700 line-clamp-1">${book.title}</h3>
                                <p class="text-xs text-slate-400">저자: ${book.author}</p>
                            </div>

                            ${targetStatus === '읽는 중' ? `
                                <div class="bg-pink-50/60 p-3 rounded-xl border border-pink-100 space-y-2">
                                    <div class="flex justify-between items-baseline text-xs">
                                        <span class="font-bold text-pink-800">Today 목표</span>
                                        <span class="text-[11px] text-pink-500">남은 날: ${calc.remainingDays}일</span>
                                    </div>
                                    <div class="text-lg font-bold text-purple-600">
                                        ${calc.dailyTarget} <span class="text-xs font-normal text-slate-500">페이지 / 일</span>
                                    </div>
                                    
                                    <div class="space-y-1">
                                        <div class="flex justify-between text-[11px] text-slate-400">
                                            <span>진행률</span>
                                            <span>${progressPct}% (${book.current_page}/${book.total_pages}p)</span>
                                        </div>
                                        <div class="w-full bg-purple-100/60 h-2 rounded-full overflow-hidden">
                                            <div class="bg-gradient-to-r from-pink-400 to-purple-400 h-full rounded-full transition-all duration-300" style="width: ${progressPct}%"></div>
                                        </div>
                                    </div>
                                </div>

                                <div class="flex items-center gap-2 pt-1">
                                    <input type="number" id="page-input-${book.id}" value="${book.current_page}" min="0" max="${book.total_pages}"
                                        class="w-full text-xs p-2 rounded-xl border border-purple-100 focus:outline-none focus:ring-1 focus:ring-purple-300 bg-white/90">
                                    <button onclick="updateBookPage(${book.id})" 
                                        class="bg-gradient-to-r from-pink-400 to-purple-400 hover:opacity-90 text-white font-semibold text-xs py-2 px-3 rounded-xl shadow-xs transition-all whitespace-nowrap">
                                        기록
                                    </button>
                                </div>
                            ` : ''}

                            ${targetStatus === '읽기 완료' ? `
                                <div class="bg-purple-50/80 p-3 rounded-xl border border-purple-100 text-center space-y-1">
                                    <p class="text-xs font-bold text-purple-700">🎉 축하합니다! 완독했습니다</p>
                                    <p class="text-[11px] text-purple-400">총 ${book.total_pages} 페이지 완료</p>
                                </div>
                            ` : ''}

                            ${targetStatus === '읽고 싶음' ? `
                                <div class="text-xs text-slate-400 space-y-1">
                                    <p>총 페이지: ${book.total_pages}p</p>
                                    <p>목표 완료일: ${book.target_date}</p>
                                </div>
                                <button onclick="startReading(${book.id})" 
                                    class="w-full bg-gradient-to-r from-purple-500 to-indigo-500 hover:opacity-90 text-white font-semibold text-xs py-2 rounded-xl shadow-xs transition-all">
                                    📖 지금 읽기 시작
                                </button>
                            ` : ''}
                        </div>
                    </div>
                `;
            }).join('');
        }

        function updateBookPage(bookId) {
            const input = document.getElementById(`page-input-${bookId}`);
            const newPage = parseInt(input.value) || 0;

            const book = books.find(b => b.id === bookId);
            if (!book) return;

            book.current_page = Math.min(newPage, book.total_pages);

            if (book.current_page >= book.total_pages) {
                book.status = '읽기 완료';
                confetti({
                    particleCount: 100,
                    spread: 70,
                    origin: { y: 0.6 }
                });
                alert(`🎉 축하합니다! '${book.title}' 책을 완독하셨습니다!`);
            }

            updateStats();
            renderCalendar();
            renderBooks();
        }

        function startReading(bookId) {
            const book = books.find(b => b.id === bookId);
            if (book) {
                book.status = '읽는 중';
                updateStats();
                switchTab('reading');
            }
        }

        function switchTab(tab) {
            currentTab = tab;
            document.querySelectorAll('.tab-btn').forEach(btn => {
                btn.classList.remove('border-pink-500', 'text-pink-600', 'border-purple-500', 'text-purple-700');
                btn.classList.add('border-transparent', 'text-slate-500');
            });

            const activeBtn = document.getElementById(`tabBtn-${tab}`);
            if (activeBtn) {
                activeBtn.classList.remove('border-transparent', 'text-slate-500');
                if (tab === 'python') {
                    activeBtn.classList.add('border-purple-500', 'text-purple-700');
                } else {
                    activeBtn.classList.add('border-pink-500', 'text-pink-600');
                }
            }

            renderBooks();
        }

        function updateStats() {
            document.getElementById('statReading').textContent = books.filter(b => b.status === '읽는 중').length;
            document.getElementById('statCompleted').textContent = books.filter(b => b.status === '읽기 완료').length;
            document.getElementById('statWishlist').textContent = books.filter(b => b.status === '읽고 싶음').length;
        }

        function copyPythonCode() {
            const codeText = document.getElementById('pythonCodeBlock').innerText;
            navigator.clipboard.writeText(codeText).then(() => {
                alert('Streamlit main.py 소스코드가 클립보드에 복사되었습니다!');
            }).catch(() => {
                alert('복사 중 오류가 발생했습니다.');
            });
        }
    </script>
</body>
</html>
```eof

The UI and calendar view have been updated:

1. **Soft Pink & Purple Pastel Gradient Theme**: Updated the global canvas, cards, buttons, badges, and controls with a soft pink (`#fdf2f8`), lavender (`#f3e8ff`), and soft indigo pastel background gradient with glassmorphism effects.
2. **Clean & Refined Calendar Lines**: Designed a crisp, 1px thin grid divider layout with soft purple border highlights (`border-purple-100`), clean cell spacing, and subtle hover interactions.
3. **Interactive Book Milestones on Calendar**: Selected books now visually plot onto their target completion dates with pastel badges so you can easily track your schedule month by month.
