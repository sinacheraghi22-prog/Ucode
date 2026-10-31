import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, Code2, Database, BrainCircuit, Loader2 } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import axios from 'axios';

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState('basic');
  const [targetCol, setTargetCol] = useState('');
  const fileInputRef = useRef(null);

  // هندل کردن آپلود فایل و ارسال به بک‌اند
  const handleUpload = async (e) => {
    const selectedFile = e.target.files[0];
    if (!selectedFile) return;
    
    setFile(selectedFile);
    fetchCode(selectedFile, activeTab, targetCol);
  };

  const fetchCode = async (f, gen, target) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', f);
    formData.append('generator', gen);
    if (target) formData.append('target_col', target);

    try {
      const res = await axios.post('https://ucode-fyvp.onrender.com/api/generate', formData);
      setData(res.data);
      if (res.data.schema.columns.length > 0 && !target) {
        setTargetCol(res.data.schema.columns[0].name); // پیش‌فرض برای ML
      }
    } catch (err) {
      console.error(err);
      const errorMsg = err.response?.data?.detail || "خطا در ارتباط با سرور بک‌اند. آیا FastAPI روشن است؟";
      alert(errorMsg);
    }
    setLoading(false);
  };

  const changeTab = (tab) => {
    setActiveTab(tab);
    if (file) fetchCode(file, tab, targetCol);
  };

  return (
    <div className="min-h-screen relative overflow-hidden flex flex-col items-center py-12 px-4">
      {/* پس‌زمینه سه‌بعدی متحرک (توپ‌های نورانی) */}
      <motion.div 
        animate={{ x: [0, 50, 0], y: [0, -50, 0] }} 
        transition={{ duration: 10, repeat: Infinity, ease: "linear" }}
        className="absolute top-10 left-10 w-96 h-96 bg-indigo-600/30 rounded-full blur-[120px] pointer-events-none"
      />
      <motion.div 
        animate={{ x: [0, -60, 0], y: [0, 60, 0] }} 
        transition={{ duration: 12, repeat: Infinity, ease: "linear" }}
        className="absolute bottom-10 right-10 w-96 h-96 bg-purple-600/30 rounded-full blur-[120px] pointer-events-none"
      />

      {/* هدر */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12 z-10">
        <h1 className="text-5xl font-extrabold mb-4 tracking-tight">
          ⚡ <span className="text-gradient">Ucode</span>
        </h1>
        <p className="text-gray-400 text-lg max-w-xl mx-auto">
          فایل اکسل خود را آپلود کنید و کدهای پایتون، تحلیل داده و یادگیری ماشین را با یک کلیک دریافت کنید.
        </p>
      </motion.div>

      {/* باکس آپلود شیشه‌ای */}
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }} 
        animate={{ opacity: 1, scale: 1 }} 
        className="glass-panel w-full max-w-3xl p-10 rounded-3xl flex flex-col items-center justify-center cursor-pointer hover:border-indigo-500/50 transition-colors z-10"
        onClick={() => fileInputRef.current.click()}
      >
        <input type="file" accept=".xlsx, .xls" className="hidden" ref={fileInputRef} onChange={handleUpload} />
        {loading ? (
          <Loader2 className="w-16 h-16 text-indigo-500 animate-spin mb-4" />
        ) : (
          <UploadCloud className="w-16 h-16 text-indigo-400 mb-4" />
        )}
        <h2 className="text-xl font-semibold mb-2 text-center">
          {file ? file.name : "برای آپلود فایل کلیک کنید"}
        </h2>
        <p className="text-gray-500 text-sm">فرمت‌های مجاز: .xlsx, .xls</p>
      </motion.div>

      {/* بخش نمایش نتایج */}
      <AnimatePresence>
        {data && !loading && (
          <motion.div 
            initial={{ opacity: 0, y: 40 }} 
            animate={{ opacity: 1, y: 0 }} 
            className="w-full max-w-5xl mt-12 z-10"
          >
            {/* خلاصه ساختار فایل */}
            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="glass-panel p-4 rounded-2xl text-center">
                <p className="text-gray-400 text-sm">ردیف‌ها</p>
                <p className="text-2xl font-bold text-indigo-400">{data.schema.n_rows}</p>
              </div>
              <div className="glass-panel p-4 rounded-2xl text-center">
                <p className="text-gray-400 text-sm">ستون‌ها</p>
                <p className="text-2xl font-bold text-purple-400">{data.schema.n_cols}</p>
              </div>
              <div className="glass-panel p-4 rounded-2xl text-center">
                <p className="text-gray-400 text-sm">شیت فعال</p>
                <p className="text-2xl font-bold text-pink-400">{data.schema.active_sheet}</p>
              </div>
            </div>

            {/* تب‌ها */}
            <div className="flex gap-4 mb-6 flex-wrap">
              {[
                { id: 'basic', label: 'پایتون پایه', icon: Code2 },
                { id: 'eda', label: 'تحلیل داده', icon: Database },
                { id: 'ml', label: 'یادگیری ماشین', icon: BrainCircuit }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => changeTab(tab.id)}
                  className={`flex items-center gap-2 px-6 py-3 rounded-xl font-semibold transition-all ${
                    activeTab === tab.id 
                    ? 'bg-indigo-600 text-white shadow-[0_0_20px_rgba(79,70,229,0.4)]' 
                    : 'glass-panel text-gray-400 hover:text-white'
                  }`}
                >
                  <tab.icon className="w-5 h-5" />
                  {tab.label}
                </button>
              ))}
            </div>

            {/* انتخاب ستون هدف برای ML */}
            {activeTab === 'ml' && (
              <div className="glass-panel p-4 rounded-xl mb-6 flex items-center gap-4 flex-wrap">
                <label className="text-gray-300">ستون هدف (Target):</label>
                <select 
                  className="bg-black/50 border border-gray-700 text-white rounded-lg px-4 py-2 outline-none"
                  value={targetCol}
                  onChange={(e) => {
                    setTargetCol(e.target.value);
                    fetchCode(file, 'ml', e.target.value);
                  }}
                >
                  {data.schema.columns.map(c => (
                    <option key={c.name} value={c.name}>{c.name}</option>
                  ))}
                </select>
              </div>
            )}

            {/* نمایش کدها */}
            <div className="space-y-6">
              {data.sections.map((sec, idx) => (
                <motion.div 
                  key={idx} 
                  initial={{ opacity: 0, y: 20 }} 
                  animate={{ opacity: 1, y: 0 }} 
                  transition={{ delay: idx * 0.1 }}
                  className="glass-panel rounded-2xl overflow-hidden"
                >
                  <div className="p-4 border-b border-white/10 bg-white/5">
                    <h3 className="font-bold text-lg text-indigo-300">{sec.title}</h3>
                  </div>
                  <div className="p-4">
                    <SyntaxHighlighter language="python" style={vscDarkPlus} customStyle={{ borderRadius: '12px', margin: 0, fontSize: '14px' }}>
                      {sec.code}
                    </SyntaxHighlighter>
                    <div className="mt-4 text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">
                      {sec.explanation}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}