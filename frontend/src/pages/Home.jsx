import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MessageSquare, Files, Scale, ArrowRight, Sparkles, Zap, Heart, Star, Users, Award, Clock, Shield } from 'lucide-react';

const Home = () => {
  const [currentFeature, setCurrentFeature] = useState(0);

  const features = [
    {
      icon: MessageSquare,
      title: 'AI Chat Asistent',
      description: 'Postavite pitanja o Zakonu o radu FBiH i dobijte precizne odgovore sa automatskim pristupom internetu kada je potrebno.',
      color: 'from-blue-500 to-cyan-500',
      href: '/chat',
      stats: '1000+ odgovora dnevno'
    },
    {
      icon: Files,
      title: 'Analiza dokumenata',
      description: 'Upload-ujte ugovore o radu ili druge dokumente i dobijte detaljnu AI analizu usklađenosti sa Zakonom o radu.',
      color: 'from-purple-500 to-pink-500',
      href: '/compare',
      stats: '95% tačnost analize'
    },
  ];

  const stats = [
    { value: '150+', label: 'Članova zakona', icon: Scale, color: 'text-blue-600' },
    { value: '24/7', label: 'Dostupnost', icon: Clock, color: 'text-green-600' },
    { value: '99%', label: 'Tačnost odgovora', icon: Shield, color: 'text-purple-600' },
    { value: '1000+', label: 'Korisnika', icon: Users, color: 'text-pink-600' }
  ];

  const testimonials = [
    {
      name: "Emir Begović",
      role: "Vlasnik male IT firme",
      content: "Kao vlasnik male firme, nemam vremena ni budžet za stalnog pravnika. Ova analiza je kao da imam pravnog savjetnika u džepu! Kada spremam ugovor za novog programera, samo ga provučem kroz sistem i odmah vidim da li sam zaboravio nešto važno. Najjače mi je što objašnjava sve na bosanskom i daje mi hitne akcije koje treba da preduzmem. Preporučujem svim preduzetnicima!",
      rating: 5
    },
    {
      name: "Ana Marković", 
      role: "HR menadžerka",
      content: "Ova AI analiza mi je revolucionirala posao! Ranije sam morala satima čitati Zakon o radu da provjerim da li je ugovor ispravan. Sada samo uploadujem dokument i za minut znam šta nedostaje. Posebno mi je korisno što mi pokazuje konkretne članke zakona i daje preporuke šta da popravim. Spasila me je od nekoliko grešaka koje bi mogle koštati firmu!",
      rating: 5
    },
    {
      name: "Selma Kurtović",
      role: "Ekonomistkinja u potrazi za poslom", 
      content: "Konačno imam način da provjerim da li me poslodavac pokušava prevariti! Kad sam dobila ponudu gdje nije spomenut godišnji odmor, analiza mi je pokazala da to mora biti u ugovoru prema zakonu. Otišla sam nazad i zatražila ispravku - i dobila sam je! Sistem mi je dao samopouzdanje da znam svoja prava. Sada prije svakog razgovora za posao proverim njihovu ponudu.",
      rating: 5
    }
  ];

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % features.length);
    }, 4000);
    return () => clearInterval(interval);
  }, [features.length]);

  return (
    <div className="pt-20 min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-purple-50">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-24">
        {/* Animated Background Elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-gradient-to-r from-blue-200/30 to-purple-200/30 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-gradient-to-r from-purple-200/30 to-pink-200/30 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
          <div className="absolute bottom-1/4 left-1/2 w-96 h-96 bg-gradient-to-r from-cyan-200/30 to-blue-200/30 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '4s' }}></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-6 text-center">
          <div className="animate-fade-in">
            {/* Badge */}
            <div className="inline-flex items-center px-8 py-4 bg-white/90 backdrop-blur-sm shadow-lg border border-blue-100 rounded-full text-blue-700 text-sm font-semibold mb-8 hover:shadow-xl transition-all duration-300">
              <Sparkles className="h-4 w-4 mr-2 text-blue-500" />
              Najnapredniji AI pravni asistent za FBiH
              <Zap className="h-4 w-4 ml-2 text-yellow-500" />
            </div>
            
            {/* Main Heading */}
            <h1 className="text-6xl md:text-8xl font-bold mb-8 leading-tight">
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Pravni Asistent
              </span>
              <br />
              <span className="text-4xl md:text-5xl text-slate-700 font-light">
                za Zakon o radu FBiH
              </span>
            </h1>
            
            {/* Description */}
            <p className="text-xl md:text-2xl text-slate-600 max-w-4xl mx-auto leading-relaxed mb-12">
              Revolucionarni AI asistent koji vam pomaže da razumijete i primijenite 
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent font-semibold"> Zakon o radu Federacije Bosne i Hercegovine</span>. 
              Brzo, precizno, dostupno 24/7.
            </p>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16">
              <Link
                to="/chat"
                className="group relative inline-flex items-center px-10 py-5 text-xl font-bold text-white rounded-3xl overflow-hidden transform hover:scale-105 transition-all duration-300 shadow-2xl hover:shadow-3xl"
              >
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600"></div>
                <div className="absolute inset-0 bg-gradient-to-r from-blue-700 via-purple-700 to-pink-700 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                <div className="relative flex items-center space-x-3">
                  <MessageSquare className="h-6 w-6" />
                  <span>Započni razgovor</span>
                  <ArrowRight className="h-6 w-6 group-hover:translate-x-2 transition-transform" />
                </div>
              </Link>
              
              <Link
                to="/compare"
                className="inline-flex items-center px-10 py-5 text-xl font-semibold bg-white/90 backdrop-blur-sm border border-slate-200 text-slate-700 rounded-3xl hover:bg-white hover:shadow-xl transition-all duration-300 group"
              >
                <Files className="h-6 w-6 mr-3 text-purple-600" />
                <span>Analiziraj dokument</span>
                <ArrowRight className="h-5 w-5 ml-3 group-hover:translate-x-1 transition-transform text-purple-600" />
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => {
              const Icon = stat.icon;
              return (
                <div
                  key={stat.label}
                  className="text-center bg-white/80 backdrop-blur-sm border border-slate-200 rounded-2xl p-8 shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-300"
                  style={{ animationDelay: `${index * 0.1}s` }}
                >
                  <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-slate-100 to-slate-200 mb-4">
                    <Icon className={`h-8 w-8 ${stat.color}`} />
                  </div>
                  <div className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                    {stat.value}
                  </div>
                  <div className="text-slate-600 font-medium">
                    {stat.label}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-5xl md:text-6xl font-bold mb-6">
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">Kako vam možemo pomoći?</span>
            </h2>
            <p className="text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
              Naš AI asistent pruža glavne usluge za sve vaše potrebe vezane za Zakon o radu
            </p>
          </div>

          {/* Centričane kartice - 2 u redu */}
          <div className="flex justify-center">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 max-w-5xl w-full">
              {features.map((feature, index) => {
                const Icon = feature.icon;
                return (
                  <div
                    key={feature.title}
                    className="group relative"
                    style={{ animationDelay: `${index * 0.2}s` }}
                  >
                    <Link
                      to={feature.href}
                      className="block w-full bg-white/90 backdrop-blur-sm border border-slate-200 rounded-3xl p-8 h-full shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300"
                    >
                      {/* Animated Background */}
                      <div className={`absolute top-0 left-0 right-0 h-2 bg-gradient-to-r ${feature.color} rounded-t-3xl`}></div>
                      
                      {/* Icon */}
                      <div className={`inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br ${feature.color} rounded-3xl mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg`}>
                        <Icon className="h-10 w-10 text-white" />
                      </div>
                      
                      {/* Content */}
                      <h3 className="text-2xl font-bold text-slate-800 mb-4 group-hover:text-blue-600 transition-colors">
                        {feature.title}
                      </h3>
                      
                      <p className="text-slate-600 leading-relaxed mb-6">
                        {feature.description}
                      </p>

                      {/* Stats */}
                      <div className="inline-flex items-center px-4 py-2 bg-slate-100 rounded-full text-sm font-medium text-slate-700 mb-4">
                        <Award className="h-4 w-4 mr-2 text-yellow-500" />
                        {feature.stats}
                      </div>
                      
                      {/* CTA */}
                      <div className="flex items-center justify-center text-blue-600 font-semibold group-hover:translate-x-2 transition-transform duration-300">
                        <span>Započni sada</span>
                        <ArrowRight className="h-5 w-5 ml-2" />
                      </div>
                    </Link>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-24 bg-gradient-to-br from-blue-50/80 to-purple-50/80">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-20">
            <h2 className="text-5xl font-bold mb-6">
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">Šta kažu korisnici</span>
            </h2>
            <p className="text-xl text-slate-600">
              Pridružite se hiljadama zadovoljnih korisnika
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div
                key={index}
                className="bg-white/90 backdrop-blur-sm border border-slate-200 rounded-3xl p-8 shadow-lg hover:shadow-2xl transform hover:scale-105 transition-all duration-300"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                {/* Stars */}
                <div className="flex items-center mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="h-5 w-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                
                {/* Quote */}
                <p className="text-slate-600 leading-relaxed mb-6 italic">
                  "{testimonial.content}"
                </p>
                
                {/* Author */}
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-bold mr-4 shadow-lg">
                    {testimonial.name.charAt(0)}
                  </div>
                  <div>
                    <div className="font-semibold text-slate-800">
                      {testimonial.name}
                    </div>
                    <div className="text-slate-500 text-sm">
                      {testimonial.role}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-24">
        <div className="max-w-5xl mx-auto px-6 text-center">
          <div className="relative bg-white/80 backdrop-blur-sm border border-slate-200 rounded-3xl p-16 overflow-hidden shadow-2xl">
            {/* Background Animation */}
            <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 via-purple-600/5 to-pink-600/5"></div>
            
            <div className="relative">
              <h2 className="text-5xl md:text-6xl font-bold mb-6">
                <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">Spremni za početak?</span>
              </h2>
              <p className="text-2xl text-slate-600 mb-10 leading-relaxed">
                Pridružite se hiljadama korisnika koji već koriste 
                <br />naš AI pravni asistent
              </p>
              
              <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
                <Link
                  to="/chat"
                  className="group inline-flex items-center px-10 py-5 text-xl font-bold text-white rounded-3xl bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 shadow-2xl hover:shadow-3xl transform hover:scale-105 transition-all duration-300"
                >
                  <MessageSquare className="h-6 w-6 mr-3" />
                  <span>Započni chat</span>
                  <Sparkles className="h-6 w-6 ml-3" />
                </Link>
                
                <Link
                  to="/compare"
                  className="inline-flex items-center px-10 py-5 text-xl font-semibold bg-white/90 backdrop-blur-sm border border-slate-200 text-slate-700 rounded-3xl hover:bg-white hover:shadow-xl transition-all duration-300"
                >
                  <Files className="h-6 w-6 mr-3 text-purple-600" />
                  <span>Analiziraj dokument</span>
                </Link>
              </div>
              
              {/* Love Note */}
              <div className="mt-12 flex items-center justify-center text-slate-500">
                <span>Napravljeno sa</span>
                <Heart className="h-5 w-5 mx-2 text-red-500 fill-current animate-pulse" />
                <span>u Zenici, BiH</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;