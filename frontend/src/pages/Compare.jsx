import React, { useState, useRef, useCallback } from 'react';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  XCircle, 
  Download,
  RefreshCw,
  Scale,
  Calendar,
  DollarSign,
  Clock,
  User,
  Building,
  Award,
  AlertTriangle,
  Shield,
  Info
} from 'lucide-react';

const FIELD_LABELS = {
  salary: { label: "Plata", icon: <DollarSign className="w-5 h-5" />, unit: "" },
  working_hours: { label: "Radno vrijeme", icon: <Clock className="w-5 h-5" />, unit: "sati" },
  vacation_days: { label: "Godišnji odmor", icon: <Calendar className="w-5 h-5" />, unit: "dana" },
  notice_period: { label: "Otkazni rok", icon: <Calendar className="w-5 h-5" />, unit: "dana" },
  probation_period: { label: "Probni rad", icon: <Award className="w-5 h-5" />, unit: "mjeseci" },
};

const ALL_DOC_LABELS = {
  document_type: { label: "Tip dokumenta", icon: <FileText className="w-4 h-4" /> },
  company_name: { label: "Kompanija", icon: <Building className="w-4 h-4" /> },
  employee_name: { label: "Radnik", icon: <User className="w-4 h-4" /> },
  position: { label: "Pozicija", icon: <Award className="w-4 h-4" /> },
  salary: { label: "Plata", icon: <DollarSign className="w-4 h-4" /> },
  currency: { label: "Valuta", icon: <DollarSign className="w-4 h-4" /> },
  working_hours: { label: "Radno vrijeme", icon: <Clock className="w-4 h-4" /> },
  probation_period: { label: "Probni rad", icon: <Award className="w-4 h-4" /> },
  vacation_days: { label: "Godišnji odmor", icon: <Calendar className="w-4 h-4" /> },
  notice_period: { label: "Otkazni rok", icon: <Calendar className="w-4 h-4" /> },
  contract_type: { label: "Tip ugovora", icon: <Scale className="w-4 h-4" /> },
  start_date: { label: "Datum početka", icon: <Calendar className="w-4 h-4" /> },
  workplace: { label: "Mjesto rada", icon: <Building className="w-4 h-4" /> },
};

const Compare = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState('');
  const [dragActive, setDragActive] = useState(false);
  const fileInputRef = useRef(null);

  // Drag and drop handlers
  const handleDrag = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragleave" || e.type === "dragover") {
      setDragActive(e.type !== "dragleave");
    }
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      validateAndSetFile(file);
    }
  }, []);

  const validateAndSetFile = (file) => {
    const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    const maxSize = 10 * 1024 * 1024;
    if (!allowedTypes.includes(file.type)) {
      setError('Nepodržan tip fajla. Molimo uploadujte PDF, PNG, JPG, JPEG, GIF ili WEBP fajl.');
      return;
    }
    if (file.size > maxSize) {
      setError('Fajl je prevelik. Maksimalna veličina je 10MB.');
      return;
    }
    setSelectedFile(file);
    setError('');
    setAnalysisResult(null);
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const analyzeDocument = async () => {
    if (!selectedFile) {
      setError('Molimo odaberite fajl za analizu.');
      return;
    }
    setIsAnalyzing(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('document', selectedFile);
      const response = await fetch('http://localhost:5000/api/analyze_document', {
        method: 'POST',
        body: formData,
      });
      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.error || 'Greška prilikom analize dokumenta');
        setIsAnalyzing(false);
        return;
      }
      const result = await response.json();
      if (result.success) {
        setAnalysisResult(result);
      } else {
        setError(result.error || 'Greška prilikom analize dokumenta');
      }
    } catch (err) {
      setError('Došlo je do greške prilikom analize dokumenta. Molimo pokušajte ponovo.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setSelectedFile(null);
    setAnalysisResult(null);
    setError('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // === Status helper functions ===
  function getStatusColor(status) {
    if (!status) return { bg: 'bg-gray-100', text: 'text-gray-600', icon: Info };
    const statusLower = status.toLowerCase();
    if (statusLower.includes('usklađeno') && !statusLower.includes('nije')) {
      return { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', icon: CheckCircle };
    }
    if (statusLower.includes('nije')) {
      return { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', icon: XCircle };
    }
    return { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', icon: AlertTriangle };
  }

  function getOverallComplianceScore() {
    const analysis = analysisResult?.compliance_analysis?.legal_compliance_analysis;
    if (!analysis) return { score: 0, total: 0 };
    
    let compliant = 0;
    let total = 0;
    
    Object.values(analysis).forEach(field => {
      if (field?.status) {
        total++;
        if (field.status.toLowerCase().includes('usklađeno') && !field.status.toLowerCase().includes('nije')) {
          compliant++;
        }
      }
    });
    
    return { score: compliant, total };
  }

  // === Enhanced value formatting ===
  const formatValue = (field, value, currency) => {
    if (!value || value === "" || value === null) return "Nije navedeno";
    
    if (field === "salary" && currency) {
      return `${value} ${currency}`;
    }
    if (field === "working_hours") {
      return `${value} sati`;
    }
    if (field === "vacation_days") {
      return `${value} dana`;
    }
    if (field === "notice_period") {
      return `${value} dana`;
    }
    if (field === "probation_period") {
      return `${value} mjeseci`;
    }
    return value;
  };

  // === Prikaz detalja dokumenta ===
  const renderDocumentInfo = () => {
    const doc = analysisResult?.document;
    if (!doc) return null;
    
    return (
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-8 py-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white/20 rounded-lg">
              <FileText className="w-6 h-6 text-white" />
            </div>
            <div>
              <h3 className="text-xl font-semibold text-white">Izvučeni podaci iz dokumenta</h3>
              <p className="text-blue-100 text-sm mt-1">Strukturirane informacije iz vašeg ugovora</p>
            </div>
          </div>
        </div>
        
        <div className="p-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(ALL_DOC_LABELS).map(([field, meta]) => (
              <InfoCard
                key={field}
                label={meta.label}
                value={formatValue(field, doc[field], doc.currency)}
                icon={meta.icon}
                important={['salary', 'working_hours', 'vacation_days'].includes(field)}
              />
            ))}
          </div>
        </div>
      </div>
    );
  };

  // === Enhanced compliance analysis ===
  const renderComplianceAnalysis = () => {
    const analysis = analysisResult?.compliance_analysis?.legal_compliance_analysis;
    if (!analysis) {
      return (
        <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-8">
          <div className="text-center text-slate-500">
            <Info className="w-12 h-12 mx-auto mb-4 text-slate-400" />
            <p className="text-lg font-medium">Detaljna analiza nije dostupna</p>
            <p className="text-sm mt-2">Analiza usklađenosti nije mogla biti generirana za ovaj dokument.</p>
          </div>
        </div>
      );
    }

    const { score, total } = getOverallComplianceScore();
    const percentage = total > 0 ? Math.round((score / total) * 100) : 0;

    return (
      <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
        {/* Header with score */}
        <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-white/20 rounded-lg">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-semibold text-white">Analiza usklađenosti sa zakonom</h3>
                <p className="text-purple-100 text-sm mt-1">Detaljni pregled svih ključnih stavki</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold text-white">{percentage}%</div>
              <div className="text-purple-100 text-sm">{score} od {total} usklađeno</div>
            </div>
          </div>
        </div>

        <div className="p-8">
          <div className="space-y-8">
            {Object.entries(FIELD_LABELS).map(([field, meta]) => (
              <ComplianceField
                key={field}
                field={field}
                label={meta.label}
                icon={meta.icon}
                unit={meta.unit}
                details={analysis[field]}
                value={analysisResult?.document?.[field]}
                currency={analysisResult?.document?.currency}
              />
            ))}
          </div>
        </div>
      </div>
    );
  };

  const ComplianceField = ({ field, label, icon, unit, details, value, currency }) => {
    const statusStyle = getStatusColor(details?.status);
    const StatusIcon = statusStyle.icon;

    return (
      <div className="border border-slate-200 rounded-xl p-6 hover:shadow-md transition-shadow">
        <div className="flex items-start gap-4">
          <div className="flex-shrink-0">
            <div className="p-3 bg-slate-100 rounded-lg text-slate-600">
              {icon}
            </div>
          </div>
          
          <div className="flex-grow min-w-0">
            <div className="flex items-center gap-3 mb-3">
              <h4 className="text-lg font-semibold text-slate-900">{label}</h4>
              <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium ${statusStyle.bg} ${statusStyle.text} ${statusStyle.border} border`}>
                <StatusIcon className="w-4 h-4" />
                {details?.status || 'NEJASNO'}
              </div>
            </div>

            {value && (
              <div className="mb-4 p-3 bg-slate-50 rounded-lg">
                <span className="text-sm text-slate-600">Vrijednost iz dokumenta: </span>
                <span className="font-semibold text-slate-900">
                  {formatValue(field, value, currency)}
                </span>
              </div>
            )}

            <div className="space-y-4">
              <div>
                <h5 className="font-medium text-slate-700 mb-2 flex items-center gap-2">
                  <Info className="w-4 h-4" />
                  Pravni komentar
                </h5>
                <p className="text-slate-600 leading-relaxed">
                  {details?.comment || 'Nema dodatnih informacija o usklađenosti ovog polja.'}
                </p>
              </div>

              <div>
                <h5 className="font-medium text-blue-700 mb-2 flex items-center gap-2">
                  <Scale className="w-4 h-4" />
                  Preporuka
                </h5>
                <p className="text-blue-600 leading-relaxed">
                  {details?.advice || 'Nema specifičnih preporuka za ovo polje.'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const InfoCard = ({ icon, label, value, important = false }) => (
    <div className={`rounded-xl p-4 border transition-all hover:shadow-sm ${
      important 
        ? 'bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200' 
        : 'bg-slate-50 border-slate-200'
    }`}>
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-lg ${
          important ? 'bg-blue-100 text-blue-600' : 'bg-slate-200 text-slate-500'
        }`}>
          {icon}
        </div>
        <div className="min-w-0 flex-1">
          <div className={`text-sm font-medium mb-1 ${
            important ? 'text-blue-700' : 'text-slate-600'
          }`}>
            {label}
          </div>
          <div className={`font-semibold text-sm break-words ${
            important ? 'text-blue-900' : 'text-slate-900'
          }`}>
            {value}
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-3 mb-6">
            <div className="p-3 bg-blue-600 rounded-2xl">
              <Scale className="w-8 h-8 text-white" />
            </div>
            <br />
            <br /> <br /><br />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-slate-900 to-slate-700 bg-clip-text text-transparent">
              Analiza usklađenosti dokumenta
            </h1>
          </div>
          <p className="text-lg text-slate-600 max-w-3xl mx-auto leading-relaxed">
            Uploadujte vaš radni dokument za detaljnu analizu usklađenosti sa Zakonom o radu Federacije BiH. 
            Naša napredna AI analiza će provjeriti sve ključne stavke i dati vam jasne preporuke.
          </p>
        </div>

        {/* Upload section */}
        {!analysisResult && (
          <div className="max-w-3xl mx-auto mb-12">
            <div
              className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all duration-300 ${
                dragActive
                  ? 'border-blue-400 bg-blue-50 scale-105'
                  : 'border-slate-300 hover:border-slate-400 hover:bg-slate-50'
              }`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
            >
              <input
                ref={fileInputRef}
                type="file"
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                onChange={handleFileSelect}
                accept=".pdf,.png,.jpg,.jpeg,.gif,.webp"
              />
              
              <div className="space-y-6">
                <div className="flex justify-center">
                  <div className={`p-6 rounded-2xl transition-colors ${
                    dragActive ? 'bg-blue-100' : 'bg-slate-100'
                  }`}>
                    <Upload className={`w-16 h-16 ${
                      dragActive ? 'text-blue-500' : 'text-slate-400'
                    }`} />
                  </div>
                </div>
                
                <div>
                  <h3 className="text-2xl font-semibold text-slate-900 mb-2">
                    {selectedFile ? selectedFile.name : 'Dodajte dokument za analizu'}
                  </h3>
                  <p className="text-slate-600 text-lg">
                    {selectedFile
                      ? 'Dokument je spreman za detaljnu analizu'
                      : 'Povucite i otpustite dokument ovdje ili kliknite da odaberete'
                    }
                  </p>
                </div>
                
                <div className="bg-white rounded-xl p-4 inline-block">
                  <p className="text-sm text-slate-500">
                    <strong>Podržani formati:</strong> PDF, PNG, JPG, JPEG, GIF, WEBP
                  </p>
                  <p className="text-sm text-slate-500">
                    <strong>Maksimalna veličina:</strong> 10MB
                  </p>
                </div>
              </div>
            </div>

            {/* Action buttons */}
            <div className="flex justify-center gap-4 mt-8">
              <button
                onClick={analyzeDocument}
                disabled={!selectedFile || isAnalyzing}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 font-semibold text-lg shadow-lg hover:shadow-xl transition-all"
              >
                {isAnalyzing ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    Analiziram dokument...
                  </>
                ) : (
                  <>
                    <Shield className="w-5 h-5" />
                    Pokreni analizu
                  </>
                )}
              </button>
              
              {selectedFile && (
                <button
                  onClick={resetAnalysis}
                  className="px-8 py-4 bg-slate-200 text-slate-700 rounded-xl hover:bg-slate-300 flex items-center gap-3 font-semibold text-lg transition-all"
                >
                  <RefreshCw className="w-5 h-5" />
                  Poništi
                </button>
              )}
            </div>
          </div>
        )}

        {/* Error message */}
        {error && (
          <div className="max-w-3xl mx-auto mb-8">
            <div className="bg-red-50 border border-red-200 rounded-xl p-6">
              <div className="flex items-center gap-3">
                <XCircle className="w-6 h-6 text-red-500 flex-shrink-0" />
                <div>
                  <h4 className="font-semibold text-red-900 mb-1">Greška prilikom analize</h4>
                  <p className="text-red-700">{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Results section */}
        {analysisResult && (
          <div className="space-y-8">
            {/* Success header */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-200 p-6">
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-4">
                  <div className="p-3 bg-green-100 rounded-xl">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold text-slate-900">
                      Analiza uspješno završena
                    </h3>
                    <p className="text-slate-600">
                      Dokument: <span className="font-medium">{selectedFile?.name}</span>
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={() => window.print()}
                    className="px-6 py-3 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 flex items-center gap-2 font-medium transition-colors"
                  >
                    <Download className="w-4 h-4" />
                    Preuzmi izvještaj
                  </button>
                  <button
                    onClick={resetAnalysis}
                    className="px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 flex items-center gap-2 font-medium transition-colors"
                  >
                    <Upload className="w-4 h-4" />
                    Novi dokument
                  </button>
                </div>
              </div>
            </div>

            {/* Document info */}
            {renderDocumentInfo()}

            {/* Compliance analysis */}
            {renderComplianceAnalysis()}
          </div>
        )}
      </div>
    </div>
  );
};

export default Compare;