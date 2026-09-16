import { Link } from 'react-router-dom'

const features = [
  { icon: '📄', title: 'PDF Resume Parsing', desc: 'Upload any text-based PDF and extract structured content instantly.' },
  { icon: '🎯', title: 'ATS Score Breakdown', desc: 'Get an explainable score across sections, skills, formatting, and keywords.' },
  { icon: '🔍', title: 'Job Description Matching', desc: 'Paste any job description and see TF-IDF similarity and skill overlap side by side.' },
  { icon: '💡', title: 'Smart Recommendations', desc: 'Discover the most relevant roles for your skill set with scored gap analysis.' },
  { icon: '📚', title: 'Personalised Learning Plan', desc: 'Get prioritised learning tasks with mini-projects for every skill gap.' },
  { icon: '🔒', title: 'Privacy First', desc: 'Resume text is processed for analysis. Files are not stored permanently by default.' },
]

export default function Landing() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-brand-900 via-brand-800 to-indigo-900 text-white">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 md:px-16 py-5">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-brand-400 rounded-lg flex items-center justify-center text-brand-900 font-bold text-sm">CL</div>
          <span className="font-bold text-lg">CareerLens AI</span>
        </div>
        <div className="flex items-center gap-3">
          <Link to="/login" className="text-brand-200 hover:text-white text-sm font-medium transition-colors">Sign In</Link>
          <Link to="/register" className="bg-white text-brand-700 hover:bg-brand-50 font-semibold text-sm px-4 py-2 rounded-xl transition-all">Get Started</Link>
        </div>
      </nav>

      {/* Hero */}
      <div className="text-center px-6 pt-16 pb-20">
        <span className="inline-block bg-brand-700/50 text-brand-200 text-xs font-semibold px-3 py-1.5 rounded-full mb-6 border border-brand-600/40">
          AI-Powered Career Intelligence
        </span>
        <h1 className="text-4xl md:text-6xl font-extrabold mb-5 leading-tight">
          Understand your resume.<br />
          <span className="text-brand-300">Improve your career.</span>
        </h1>
        <p className="text-brand-200 text-lg md:text-xl max-w-2xl mx-auto mb-10 leading-relaxed">
          Upload your PDF resume, match it against any job description, discover skill gaps, and get a personalised learning roadmap — all in one platform.
        </p>
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
          <Link to="/register" className="bg-white text-brand-700 hover:bg-brand-50 font-bold px-7 py-3.5 rounded-xl text-base transition-all shadow-lg">
            Analyse My Resume →
          </Link>
          <Link to="/login" className="border border-brand-500 text-white hover:bg-brand-800 font-semibold px-7 py-3.5 rounded-xl text-base transition-all">
            Sign In
          </Link>
        </div>
      </div>

      {/* Features */}
      <div className="bg-white/5 backdrop-blur-sm py-16 px-6 md:px-16">
        <h2 className="text-center text-2xl md:text-3xl font-bold mb-12">Everything you need to level up your career</h2>
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6 max-w-5xl mx-auto">
          {features.map(f => (
            <div key={f.title} className="bg-white/10 rounded-2xl p-6 hover:bg-white/15 transition-all border border-white/10">
              <div className="text-3xl mb-3">{f.icon}</div>
              <h3 className="font-bold text-base mb-1.5">{f.title}</h3>
              <p className="text-brand-200 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div className="text-center py-16 px-6">
        <h2 className="text-2xl md:text-3xl font-bold mb-4">Ready to take the next step?</h2>
        <p className="text-brand-200 mb-8">Create a free account and get your resume analysed in minutes.</p>
        <Link to="/register" className="bg-brand-400 hover:bg-brand-300 text-brand-900 font-bold px-8 py-3.5 rounded-xl text-base transition-all">
          Get Started Free
        </Link>
      </div>

      <footer className="border-t border-brand-800 px-6 py-6 text-center text-brand-400 text-sm">
        © {new Date().getFullYear()} CareerLens AI · Built with Flask + React · Scores are explanatory, not predictive.
      </footer>
    </div>
  )
}
