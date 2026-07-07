# Niskala - Indonesian NLP Preprocessor
# Bahasa Indonesia text processing for financial analysis

import re
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class IndoPreprocessor:
    """Indonesian text preprocessor for financial content"""
    
    def __init__(self):
        self.stopwords = self._load_stopwords()
        self.financial_terms = self._load_financial_terms()
        self.stock_patterns = self._compile_stock_patterns()
        logger.info("IndoPreprocessor initialized")
    
    def _load_stopwords(self) -> set:
        """Load Indonesian stopwords"""
        # Common Indonesian stopwords
        return {
            'ada', 'adalah', 'adanya', 'agar', 'akan', 'aku', 'anda',
            'antar', 'antara', 'apa', 'apabila', 'atas', 'atau', 'ataukah',
            'bagi', 'bahwa', 'bahwasanya', 'bakal', 'banget', 'banyak',
            'bagai', 'bagaimana', 'baik', 'bapak', 'baru', 'begitu',
            'belumlah', 'bene', 'bener', 'benar', 'berada', 'berarti',
            'berapa', 'berfungsi', 'berikan', 'berikut', 'berlaku',
            'berupa', 'besar', 'bestie', 'bgt', 'bilang', 'bisa',
            'bisa', 'bla', 'bli', 'bngt', 'bobot', 'bpk', 'bs',
            'btw', 'bukan', 'bukankah', 'bukanlah', 'bundle', 'bwh',
            'coba', 'cukup', 'cuma', 'cv', 'dah', 'dalam', 'dapat',
            'data', 'demi', 'demikian', 'dengan', 'deposito', 'derajat',
            'dgn', 'di', 'dia', 'diharapkan', 'dini', 'disaat', 'dll',
            'dng', 'doang', 'dri', 'drmn', 'drpd', 'dsb', 'dtg',
            'dua', 'dulu', 'eh', 'emg', 'enggak', 'entah', 'er',
            'erosi', 'gak', 'gdp', 'gimana', 'gini', 'github', 'gmn',
            'gni', 'gpp', 'grobak', 'guys', 'gwa', 'h', 'hal',
            'hanya', 'harus', 'hendak', 'hingga', 'hp', 'hrus', 'hs',
            'https', 'hw', 'i', 'ia', 'ikan', 'ilmu', 'img', 'indo',
            'indonesia', 'insya', 'iq', 'ironis', 'isa', 'istilah',
            'it', 'itu', 'iy', 'iya', 'jangan', 'jika', 'juga',
            'jujur', 'jul', 'jumat', 'juta', 'k', 'ka', 'kab',
            'kadar', 'kagak', 'karena', 'karna', 'kasih', 'kayak',
            'ke', 'kemarin', 'kemudian', 'kendati', 'kenapa', 'kepada',
            'kerap', 'kesan', 'ketika', 'khusus', 'kira', 'kita',
            'km', 'kmd', 'kmu', 'knp', 'koma', 'kondisi', 'konon',
            'koq', 'krn', 'kualitas', 'kuat', 'kudunya', 'kulkas',
            'kunjungi', 'lagi', 'lah', 'lain', 'laku', 'lalu',
            'lamanya', 'langkah', 'lanjut', 'lanjutan', 'lantaran',
            'lebih', 'lewat', 'lg', 'lgsg', 'libraries', 'liputan6',
            'lisan', 'list', 'lo', 'lobi', 'logika', 'luh', 'm',
            'ma', 'maka', 'makanya', 'makin', 'malah', 'malam',
            'manalagi', 'mandi', 'mania', 'mau', 'memang', 'memastikan',
            'membuat', 'merasa', 'mereka', 'mestinya', 'mgkin', 'mga',
            'microsoft', 'milyaran', 'minggu', 'misa', 'moga', 'mulai',
            'muncul', 'musim', 'n', 'na', 'nanti', 'naik', 'nampak',
            'nanti', 'napa', 'nasi', 'nda', 'negara', 'ng', 'ngapa',
            'nggak', 'ni', 'nia', 'niscaya', 'nm', 'nntn', 'nol',
            'nomor', 'ny', 'nyata', 'nyoba', 'oa', 'obligasi',
            'oktober', 'oleh', 'orang', 'p', 'pada', 'page',
            'pak', 'paling', 'palsu', 'pantau', 'para', 'pas',
            'pasar', 'patut', 'pd', 'pegawai', 'pengguna', 'penghasilan',
            'penting', 'per', 'perang', 'peraturan', 'perusahaan',
            'pesawat', 'pihak', 'poin', 'posisi', 'potensi', 'pp',
            'pr', 'preman', 'proses', 'provinsi', 'ps', 'pt',
            'ptba', 'ptpn', 'punya', 'pur', 'puskesmas', 'put',
            'qty', 'quotes', 'r', 'rabu', 'raisal', 'rangka',
            'rasa', 'rating', 'reksadana', 'rencana', 'rendah',
            'repot', 'risiko', 'rp', 'rs', 'rt', 'rupiah', 's',
            'saat', 'saja', 'saking', 'saling', 'sama', 'sampai',
            'sangat', 'satu', 'saya', 'script', 'sdg', 'sdh',
            'se', 'sebab', 'sebuah', 'sedang', 'sedikit', 'sehingga',
            'selain', 'selalu', 'selebihnya', 'selengkapnya', 'sementara',
            'sempat', 'sendiri', 'seorang', 'sepanjang', 'seperti',
            'sepatutnya', 'sering', 'sesuatu', 'setelah', 'setiap',
            'seusai', 'sewaktu', 'si', 'sini', 'soal', 'solusi',
            'sore', 'sr', 'ssi', 'stlh', 'subjek', 'sudah',
            'supaya', 'surat', 'sy', 'sya', 'syarat', 't',
            'ta', 'tabel', 'tadi', 'tagih', 'tahu', 'tahun',
            'tak', 'tambahan', 'tampak', 'tanah', 'tandas', 'tangan',
            'tentang', 'tentu', 'terhadap', 'terima', 'terlalu',
            'terlebih', 'termasuk', 'ternyata', 'tersedia', 'terserah',
            'tetapi', 'tgl', 'tiap', 'tidak', 'tilang', 'time',
            'tinggal', 'tinggi', 'tmn', 'tmp', 'tng', 'tnh',
            'tp', 'trading', 'trakhir', 'trus', 'tsb', 'tugas',
            'tuh', 'tunjukkan', 'tv', 'u', 'untuk', 'untung',
            'us', 'usd', 'utama', 'utk', 'v', 'valas', 'versi',
            'waduh', 'wah', 'walau', 'warga', 'waktu', 'wajib',
            'walhasil', 'wan', 'wanderlust', 'wargi', 'wartawan',
            'waspadalah', 'we', 'wib', 'wid', 'wikipedia', 'wira',
            'wiraniaga', 'wis', 'woi', 'wow', 'wkwk', 'wong',
            'woop', 'wow', 'ws', 'wtc', 'x', 'ya', 'yakin',
            'yang', 'yao', 'yayasan', 'yg', 'ygy', 'yoga',
            'yuk', 'yup', 'yy', 'z', 'zona'
        }
    
    def _load_financial_terms(self) -> Dict[str, str]:
        """Load financial term mappings"""
        return {
            'laba': 'profit',
            'rugi': 'loss',
            'saham': 'stock',
            'dividen': 'dividend',
            'deviden': 'dividend',
            'bagi hasil': 'dividend',
            'modal': 'capital',
            'aset': 'asset',
            'liabilitas': 'liability',
            'ekuitas': 'equity',
            'pendapatan': 'revenue',
            'beban': 'expense',
            'arus kas': 'cash flow',
            'neraca': 'balance sheet',
            'laba bersih': 'net profit',
            'laba kotor': 'gross profit',
            'laba operasi': 'operating profit',
            'margin': 'margin',
            'roa': 'return on assets',
            'roe': 'return on equity',
            'pe': 'price to earnings',
            'pb': 'price to book',
            'der': 'debt to equity',
            'bvps': 'book value per share',
            'eps': 'earnings per share',
            'trailing': 'trailing',
            'annualized': 'annualized',
            'yoy': 'year over year',
            'qoq': 'quarter over quarter',
            'mtd': 'month to date',
            'ytd': 'year to date',
            'ihsg': 'jakarta composite index',
            'jci': 'jakarta composite index',
            'BEI': 'indonesia stock exchange',
            'IDX': 'indonesia stock exchange',
            'oji': 'financial services authority',
            'bi rate': 'bank indonesia rate',
            'suku bunga': 'interest rate',
            'inflasi': 'inflation',
            'deflasi': 'deflation',
            'resesi': 'recession',
            'rupiah': 'idr',
            'dollar': 'usd',
            'forex': 'foreign exchange',
            'komoditas': 'commodity',
            'sawit': 'palm oil',
            'batu bara': 'coal',
            'nikel': 'nickel',
            'tembaga': 'copper',
            'emas': 'gold',
        }
    
    def _compile_stock_patterns(self) -> List[re.Pattern]:
        """Compile patterns for stock code detection"""
        patterns = [
            r'\b([A-Z]{4})\b',  # 4-letter codes like BBCA
            r'\b([A-Z]{2,5})\.JK\b',  # With .JK suffix
            r'(?:saham|stock)\s+([A-Z]{2,5})',  # After "saham" or "stock"
        ]
        return [re.compile(p) for p in patterns]
    
    def clean_text(self, text: str) -> str:
        """Clean text"""
        # Remove URLs
        text = re.sub(r'http\S+|www.\S+', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,;:!?-]', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text"""
        text = self.clean_text(text)
        tokens = text.lower().split()
        return tokens
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords"""
        return [t for t in tokens if t not in self.stopwords]
    
    def stem(self, text: str) -> str:
        """Simple stemming for Indonesian"""
        # Basic suffix removal
        suffixes = ['kan', 'an', 'i', 'lah', 'kah', 'tah', 'pun']
        words = text.split()
        stemmed = []
        
        for word in words:
            for suffix in suffixes:
                if word.endswith(suffix) and len(word) > len(suffix) + 2:
                    word = word[:-len(suffix)]
                    break
            stemmed.append(word)
        
        return ' '.join(stemmed)
    
    def extract_entities(self, text: str) -> Dict:
        """Extract named entities"""
        entities = {
            'stocks': [],
            'companies': [],
            'sectors': [],
            'macro': []
        }
        
        # Extract stock codes
        for pattern in self.stock_patterns:
            matches = pattern.findall(text)
            entities['stocks'].extend(matches)
        
        # Deduplicate
        entities['stocks'] = list(set(entities['stocks']))
        
        # Detect sectors
        sector_keywords = {
            'perbankan': 'banking',
            'bank': 'banking',
            'mining': 'mining',
            'tambang': 'mining',
            'energi': 'energy',
            'telekomunikasi': 'telecom',
            'properti': 'property',
            'konsumer': 'consumer',
            'teknologi': 'technology',
            'kesehatan': 'healthcare',
            'infrastruktur': 'infrastructure',
        }
        
        text_lower = text.lower()
        for keyword, sector in sector_keywords.items():
            if keyword in text_lower:
                entities['sectors'].append(sector)
        
        entities['sectors'] = list(set(entities['sectors']))
        
        return entities
    
    def normalize_financial_terms(self, text: str) -> str:
        """Normalize financial terms"""
        text_lower = text.lower()
        for indo_term, english_term in self.financial_terms.items():
            if indo_term in text_lower:
                text = re.sub(re.escape(indo_term), english_term, text, flags=re.IGNORECASE)
        return text
    
    def preprocess(self, text: str) -> Dict:
        """Full preprocessing pipeline"""
        cleaned = self.clean_text(text)
        tokens = self.tokenize(cleaned)
        tokens_no_stop = self.remove_stopwords(tokens)
        stemmed = self.stem(' '.join(tokens_no_stop))
        entities = self.extract_entities(text)
        normalized = self.normalize_financial_terms(cleaned)
        
        return {
            'original': text,
            'cleaned': cleaned,
            'tokens': tokens,
            'tokens_no_stopwords': tokens_no_stop,
            'stemmed': stemmed,
            'normalized': normalized,
            'entities': entities
        }
