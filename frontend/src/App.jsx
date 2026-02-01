import { useState, useEffect, useRef } from 'react'
import ReactMarkdown from 'react-markdown'

const API = '/api/demos' // backend mantém prefixo /api/demos; UI exibe "Playground"

export default function App() {
  const [assistants, setAssistants] = useState([])
  const [selected, setSelected] = useState(null)
  const [conversationId, setConversationId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [pdfFile, setPdfFile] = useState(null)
  const [uploadProgress, setUploadProgress] = useState(null)
  const bottomRef = useRef(null)
  const fileInputRef = useRef(null)

  // Estados para seção de contato interativa
  const [contactMode, setContactMode] = useState(null) // 'has-idea' ou 'needs-help'
  const [contactName, setContactName] = useState('')
  const [contactIdea, setContactIdea] = useState('')
  const [quizStep, setQuizStep] = useState(0)
  const [quizAnswers, setQuizAnswers] = useState({})
  const [projectScope, setProjectScope] = useState(null)
  const [scopeApproved, setScopeApproved] = useState(null)
  const [openFaqIndex, setOpenFaqIndex] = useState(null)

  useEffect(() => {
    fetch(`${API}/assistants`)
      .then((r) => r.json())
      .then((d) => {
        console.log('Assistentes recebidos do backend:', d.assistants)
        setAssistants(d.assistants || [])
        if (d.assistants?.length && !selected) setSelected(d.assistants[0].id)
      })
      .catch((err) => {
        console.error('Erro ao carregar assistentes:', err)
        setError('Não foi possível carregar assistentes.')
      })
  }, [])

  // Scroll automático removido - não faz mais scroll quando mensagens mudam
  // useEffect(() => {
  //   bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  // }, [messages])

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0]
    if (file) {
      // Aceita qualquer tipo de arquivo
      setPdfFile(file)
      setError(null)
    }
  }

  const startConversation = async () => {
    if (!selected) return
    setLoading(true)
    setError(null)
    setUploadProgress(null)
    if (conversationId) setMessages([])

    try {
      let conversationData

      if (pdfFile) {
        // Verifica se é PDF para processar, caso contrário apenas avisa
        if (pdfFile.name.toLowerCase().endsWith('.pdf')) {
        setUploadProgress('Processando PDF...')
        const formData = new FormData()
        formData.append('file', pdfFile)
        formData.append('agent_id', selected)

        const uploadRes = await fetch(`${API}/upload-pdf`, {
          method: 'POST',
          body: formData,
        })

        const uploadData = await uploadRes.json()
        if (!uploadRes.ok) throw new Error(uploadData.error || 'Erro ao processar PDF')

        conversationData = uploadData
        setUploadProgress('PDF processado com sucesso!')
        setTimeout(() => setUploadProgress(null), 2000)
        } else {
          // Para arquivos não-PDF, apenas cria a conversa sem processar o arquivo
          setError('Apenas arquivos PDF são processados como base de conhecimento. Outros tipos de arquivo podem ser mencionados na conversa, mas não serão analisados automaticamente.')
          const r = await fetch(`${API}/conversations`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agent_id: selected }),
          })
          conversationData = await r.json()
          if (!r.ok) throw new Error(conversationData.error || 'Erro ao criar conversa')
        }
      } else {
        const r = await fetch(`${API}/conversations`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ agent_id: selected }),
        })
        conversationData = await r.json()
        if (!r.ok) throw new Error(conversationData.error || 'Erro ao criar conversa')
      }

      setConversationId(conversationData.conversation_id)
      setMessages([])
      setPdfFile(null)
      if (fileInputRef.current) fileInputRef.current.value = ''
    } catch (e) {
      setError(e.message)
      setUploadProgress(null)
    } finally {
      setLoading(false)
    }
  }

  const sendMessage = async () => {
    const text = input.trim()
    if (!text || !conversationId || loading) return
    
    // Se houver arquivo anexado, faz upload primeiro
    let fileIds = []
    if (pdfFile) {
      try {
        setUploadProgress('Enviando arquivo...')
        const formData = new FormData()
        formData.append('file', pdfFile)
        
        const uploadRes = await fetch(`${API}/conversations/${conversationId}/upload-file`, {
          method: 'POST',
          body: formData,
        })
        
        if (!uploadRes.ok) {
          const uploadError = await uploadRes.json()
          throw new Error(uploadError.error || 'Erro ao enviar arquivo')
        }
        
        const uploadData = await uploadRes.json()
        fileIds = [uploadData.file_id]
        setUploadProgress('Arquivo enviado!')
        setTimeout(() => setUploadProgress(null), 1500)
      } catch (e) {
        setError(e.message)
        setUploadProgress(null)
        return
      }
    }
    
    setInput('')
    setPdfFile(null)
    if (fileInputRef.current) fileInputRef.current.value = ''
    setMessages((m) => [...m, { role: 'user', content: text, file: pdfFile?.name }])
    setLoading(true)
    setError(null)
    
    try {
      const r = await fetch(`${API}/conversations/${conversationId}/messages`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          content: text,
          file_ids: fileIds.length > 0 ? fileIds : undefined
        }),
      })
      const d = await r.json()
      if (!r.ok) throw new Error(d.error || 'Erro ao enviar mensagem')
      if (d.error) {
        setMessages((m) => [...m, { role: 'assistant', content: d.error, isError: true }])
      } else {
        setMessages((m) => [...m, { role: 'assistant', content: d.message }])
      }
    } catch (e) {
      setError(e.message)
      setMessages((m) => [...m, { role: 'assistant', content: e.message, isError: true }])
    } finally {
      setLoading(false)
      setUploadProgress(null)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const currentName = assistants.find((a) => a.id === selected)?.name || 'Assistente'

  const scrollTo = (id) => {
    document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' })
  }

  // Perguntas do quiz para estruturar ideia
  const quizQuestions = [
    {
      id: 'business_type',
      question: 'Qual é o tipo do seu negócio?',
      options: [
        'E-commerce / Varejo',
        'Serviços Profissionais',
        'Indústria / Manufatura',
        'Saúde / Clínicas',
        'Hospitalidade / Turismo',
        'Educação',
        'Tecnologia / SaaS',
        'Outro'
      ]
    },
    {
      id: 'main_challenge',
      question: 'Qual é o principal desafio que você quer resolver?',
      options: [
        'Atendimento ao cliente (demanda muito tempo)',
        'Processos manuais repetitivos',
        'Análise de dados e relatórios',
        'Gestão de vendas e leads',
        'Comunicação interna',
        'Análise de documentos/contratos',
        'Previsão e planejamento',
        'Outro'
      ]
    },
    {
      id: 'automation_goal',
      question: 'O que você gostaria de automatizar?',
      options: [
        'Atendimento e suporte ao cliente',
        'Processos administrativos',
        'Análise e relatórios',
        'Vendas e qualificação de leads',
        'Gestão de documentos',
        'Comunicação e agendamentos',
        'Análise de mercado e previsões',
        'Múltiplas áreas'
      ]
    },
    {
      id: 'time_saved',
      question: 'Quanto tempo você gostaria de economizar por semana?',
      options: [
        'Até 5 horas',
        '5-10 horas',
        '10-20 horas',
        'Mais de 20 horas'
      ]
    },
    {
      id: 'budget_range',
      question: 'Qual é o investimento que você está considerando?',
      options: [
        'Até R$ 5.000',
        'R$ 5.000 - R$ 15.000',
        'R$ 15.000 - R$ 50.000',
        'Acima de R$ 50.000',
        'Preciso de uma proposta personalizada'
      ]
    }
  ]

  // Função para gerar escopo baseado nas respostas
  const generateProjectScope = (answers) => {
    const businessType = answers.business_type || 'Não especificado'
    const mainChallenge = answers.main_challenge || 'Não especificado'
    const automationGoal = answers.automation_goal || 'Não especificado'
    const timeSaved = answers.time_saved || 'Não especificado'
    const budgetRange = answers.budget_range || 'Não especificado'

    let solutionType = 'Solução personalizada de IA'
    if (mainChallenge.includes('Atendimento')) {
      solutionType = 'Assistente Virtual / Chatbot Inteligente'
    } else if (mainChallenge.includes('Processos')) {
      solutionType = 'Automação de Processos (RPA)'
    } else if (mainChallenge.includes('Análise')) {
      solutionType = 'Análise de Dados com IA'
    } else if (mainChallenge.includes('Vendas')) {
      solutionType = 'SDR / Closer Automatizado'
    } else if (mainChallenge.includes('Documentos')) {
      solutionType = 'Análise Inteligente de Documentos'
    }

    return {
      businessType,
      mainChallenge,
      automationGoal,
      timeSaved,
      budgetRange,
      solutionType,
      description: `Solução de ${solutionType} para ${businessType}, focada em resolver ${mainChallenge}. O objetivo é automatizar ${automationGoal}, economizando ${timeSaved} por semana. Investimento estimado: ${budgetRange}.`
    }
  }

  // Função para abrir WhatsApp com mensagem pré-preenchida
  const sendToSDR = (message) => {
    try {
      // Número do WhatsApp da TARS (formato internacional sem +)
      const whatsappNumber = '554187497364'
      
      // Codifica a mensagem para URL
      const encodedMessage = encodeURIComponent(message)
      
      // Cria o link wa.me
      const whatsappUrl = `https://wa.me/${whatsappNumber}?text=${encodedMessage}`
      
      // Abre o WhatsApp em nova aba/janela
      window.open(whatsappUrl, '_blank')
      
      // Mostra mensagem de sucesso
      setError('Redirecionando para o WhatsApp...')
      setTimeout(() => {
        setContactMode(null)
        setContactName('')
        setContactIdea('')
        setQuizStep(0)
        setQuizAnswers({})
        setProjectScope(null)
        setScopeApproved(null)
        setError(null)
      }, 2000)
    } catch (e) {
      console.error('Erro ao abrir WhatsApp:', e)
      setError('Erro ao abrir WhatsApp. Por favor, tente novamente.')
    }
  }

  // Handlers do quiz
  const handleQuizAnswer = (questionId, answer) => {
    setQuizAnswers({ ...quizAnswers, [questionId]: answer })
    if (quizStep < quizQuestions.length - 1) {
      setQuizStep(quizStep + 1)
    } else {
      // Última pergunta respondida, gerar escopo
      const finalAnswers = { ...quizAnswers, [questionId]: answer }
      const scope = generateProjectScope(finalAnswers)
      setProjectScope(scope)
    }
  }

  const handleSubmitIdea = () => {
    if (!contactName.trim() || !contactIdea.trim()) {
      setError('Por favor, preencha todos os campos.')
      return
    }
    // Mensagem natural e estratégica para o SDR Agent processar
    const message = `Olá! Sou ${contactName} e gostaria de conversar sobre uma ideia de projeto com IA. ${contactIdea} Podem me ajudar a entender como podemos implementar isso?`
    sendToSDR(message)
  }

  const handleApproveScope = () => {
    if (!projectScope) return
    // Mensagem natural e estratégica para o SDR Agent
    const message = `Olá! Gostaria de conversar sobre um projeto de automação com IA. ` +
      `Trabalho com ${projectScope.businessType} e nosso principal desafio é ${projectScope.mainChallenge.toLowerCase()}. ` +
      `Queremos automatizar ${projectScope.automationGoal.toLowerCase()} para economizar ${projectScope.timeSaved.toLowerCase()}. ` +
      `Estamos pensando em uma solução de ${projectScope.solutionType.toLowerCase()} e nosso orçamento está na faixa de ${projectScope.budgetRange.toLowerCase()}. ` +
      `Podem me ajudar?`
    sendToSDR(message)
  }

  const handleRejectScope = () => {
    setScopeApproved(false)
  }

  const handleTryAgain = () => {
    setQuizStep(0)
    setQuizAnswers({})
    setProjectScope(null)
    setScopeApproved(null)
  }

  const handleTalkToExpert = () => {
    // Mensagem natural quando cliente quer falar diretamente
    let message = `Olá! Gostaria de conversar sobre automação com IA para meu negócio.`
    
    // Adiciona contexto do quiz se disponível, de forma natural
    if (projectScope) {
      message += ` Trabalho com ${projectScope.businessType.toLowerCase()} e nosso principal desafio é ${projectScope.mainChallenge.toLowerCase()}. ` +
        `Queremos automatizar ${projectScope.automationGoal.toLowerCase()}. ` +
        `Podem me ajudar a estruturar melhor essa ideia?`
    } else {
      message += ` Preciso de ajuda para estruturar minha ideia e entender como a IA pode ajudar meu negócio.`
    }
    
    sendToSDR(message)
  }

  // Carrossel de soluções
  const [currentSlide, setCurrentSlide] = useState(0)
  const [currentAgentSlide, setCurrentAgentSlide] = useState(0)
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const solutions = [
    {
      title: "IA como Secretária Virtual",
      subtitle: "Clínicas, Hotéis e Restaurantes",
      description: "Atendimento 24/7, agendamento automático, confirmação de reservas e lembretes. Reduza 80% do tempo da equipe com tarefas repetitivas.",
      benefit: "Economia de até R$ 15.000/mês em custos operacionais",
      icon: "📅",
      backgroundImage: "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=1920&q=80"
    },
    {
      title: "Assistente Jurídico Inteligente",
      subtitle: "Análise de Contratos e Documentos",
      description: "Análise instantânea de contratos, identificação de cláusulas críticas, comparação de documentos e respostas a dúvidas jurídicas em segundos.",
      benefit: "Redução de 70% no tempo de análise documental",
      icon: "⚖️",
      backgroundImage: "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1920&q=80"
    },
    {
      title: "SDR e Closer Automatizado",
      subtitle: "Time de Vendas Inteligente",
      description: "Qualificação automática de leads, follow-up personalizado, agendamento de reuniões e fechamento de vendas. Multiplique sua capacidade de vendas sem aumentar a equipe.",
      benefit: "Aumento de 3x na taxa de conversão de leads",
      icon: "🎯",
      backgroundImage: "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1920&q=80"
    },
    {
      title: "Análise Preditiva de Mercado",
      subtitle: "Inteligência para Decisões Estratégicas",
      description: "Previsão de tendências, análise de comportamento do consumidor, otimização de precificação e identificação de oportunidades de mercado em tempo real.",
      benefit: "Decisões baseadas em dados, não em intuição",
      icon: "📊",
      backgroundImage: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1920&q=80"
    },
    {
      title: "Automação de Processos",
      subtitle: "RPA e Workflow Inteligente",
      description: "Automatize processos repetitivos: emissão de notas fiscais, conciliação bancária, gestão de estoque, relatórios automáticos e muito mais.",
      benefit: "Economia de 40 horas/semana em processos manuais",
      icon: "⚙️",
      backgroundImage: "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=1920&q=80"
    },
    {
      title: "Assistente Pessoal Executivo",
      subtitle: "Produtividade e Organização",
      description: "Gestão de agenda, priorização de tarefas, resumo de reuniões, análise de emails e preparação de relatórios executivos automaticamente.",
      benefit: "Ganhe 10 horas/semana para focar no que importa",
      icon: "💼",
      backgroundImage: "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=1920&q=80"
    },
    {
      title: "Análise de Dados Inteligente",
      subtitle: "Business Intelligence com IA",
      description: "Transforme planilhas em insights acionáveis. Pergunte em linguagem natural e receba análises profundas, dashboards automáticos e recomendações estratégicas.",
      benefit: "Decisões 5x mais rápidas com dados em tempo real",
      icon: "📈",
      backgroundImage: "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1920&q=80"
    },
    {
      title: "Atendimento ao Cliente 24/7",
      subtitle: "Chatbot Inteligente Multilíngue",
      description: "Resolva 90% das dúvidas automaticamente, integração com WhatsApp, suporte em múltiplos idiomas e escalonamento inteligente para humanos quando necessário.",
      benefit: "Redução de 60% no tempo de resposta ao cliente",
      icon: "💬",
      backgroundImage: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1920&q=80"
    }
  ]

  const nextSlide = () => {
    setCurrentSlide((prev) => (prev + 1) % solutions.length)
  }

  const prevSlide = () => {
    setCurrentSlide((prev) => (prev - 1 + solutions.length) % solutions.length)
  }

  const goToSlide = (index) => {
    setCurrentSlide(index)
  }

  // Funções para carrossel de agentes
  const nextAgentSlide = () => {
    if (assistants.length > 0) {
      setCurrentAgentSlide((prev) => (prev + 1) % Math.ceil(assistants.length / 4))
    }
  }

  const prevAgentSlide = () => {
    if (assistants.length > 0) {
      setCurrentAgentSlide((prev) => (prev - 1 + Math.ceil(assistants.length / 4)) % Math.ceil(assistants.length / 4))
    }
  }

  const goToAgentSlide = (index) => {
    setCurrentAgentSlide(index)
  }

  // Auto-play do carrossel - reseta o timer quando o slide muda manualmente
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentSlide((prev) => (prev + 1) % solutions.length)
    }, 15000) // Muda slide a cada 15 segundos
    return () => clearInterval(interval)
  }, [currentSlide, solutions.length]) // Reseta o timer quando currentSlide muda

  return (
    <>
      {/* Nav — mesmo estilo Think TARS: Início, Quem Somos, Soluções, Contato */}
      <nav className="nav" aria-label="Navegação principal">
        <a href="#inicio" className="nav-logo" onClick={(e) => { e.preventDefault(); scrollTo('inicio'); setMobileMenuOpen(false) }}>
          Think <span>TARS</span>
        </a>
        <button 
          className="nav-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
          aria-expanded={mobileMenuOpen}
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
        <ul className={`nav-links ${mobileMenuOpen ? 'nav-links-open' : ''}`}>
          <li><a href="#inicio" onClick={(e) => { e.preventDefault(); scrollTo('inicio'); setMobileMenuOpen(false) }}>Início</a></li>
          <li><a href="#quem-somos" onClick={(e) => { e.preventDefault(); scrollTo('quem-somos'); setMobileMenuOpen(false) }}>Quem Somos</a></li>
          <li><a href="#solucoes" onClick={(e) => { e.preventDefault(); scrollTo('solucoes'); setMobileMenuOpen(false) }}>Soluções</a></li>
          <li><a href="#integracoes" onClick={(e) => { e.preventDefault(); scrollTo('integracoes'); setMobileMenuOpen(false) }}>Integrações</a></li>
          <li><a href="#playground" onClick={(e) => { e.preventDefault(); scrollTo('playground'); setMobileMenuOpen(false) }}>Playground</a></li>
          <li><a href="#faq" onClick={(e) => { e.preventDefault(); scrollTo('faq'); setMobileMenuOpen(false) }}>FAQ</a></li>
          <li><a href="#contato" onClick={(e) => { e.preventDefault(); scrollTo('contato'); setMobileMenuOpen(false) }}>Contato</a></li>
        </ul>
      </nav>

      {/* Seção Início — Hero */}
      <section id="inicio" className="hero">
        <span className="hero-badge">Tecnologia que entrega eficiência</span>
        <h1>Soluções que liberam o seu tempo</h1>
        <p>
          Conheça a Think TARS. Automação para problemas reais — criamos tecnologia que funciona de verdade para você ganhar tempo e focar no que importa.
        </p>
        <a href="#solucoes" className="hero-cta" onClick={(e) => { e.preventDefault(); scrollTo('solucoes') }}>
          Confira as Soluções
        </a>
      </section>

      {/* Seção Quem Somos */}
      <section id="quem-somos" className="section">
        <h2 className="section-title">Quem Somos</h2>
        <p className="section-subtitle">Acreditamos que só existe um recurso que é possível de escalar: o seu tempo!</p>
        <div className="quote-block">
          <span className="led" aria-hidden="true" />
          <p><strong>Criamos tecnologia que funciona de verdade.</strong> Para você ganhar tempo e focar no que importa!</p>
        </div>
        <div style={{ marginTop: '3rem', display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem' }}>
          <div style={{ padding: '2rem', background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--accent)' }}>Nossa Missão</h3>
            <p style={{ fontSize: '1.15rem', lineHeight: '1.6', color: 'var(--text-muted)' }}>
              Transformar a forma como empresas trabalham através de automação inteligente e soluções de IA que realmente entregam resultados mensuráveis.
            </p>
          </div>
          <div style={{ padding: '2rem', background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--accent)' }}>Nossa Visão</h3>
            <p style={{ fontSize: '1.15rem', lineHeight: '1.6', color: 'var(--text-muted)' }}>
              Ser referência em automação inteligente, ajudando empresas a escalar seus resultados sem aumentar proporcionalmente seus custos operacionais.
            </p>
          </div>
          <div style={{ padding: '2rem', background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)' }}>
            <h3 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--accent)' }}>Nossos Valores</h3>
            <p style={{ fontSize: '1.15rem', lineHeight: '1.6', color: 'var(--text-muted)' }}>
              Eficiência, inovação e resultados práticos. Acreditamos em tecnologia que funciona de verdade, não em promessas vazias.
            </p>
          </div>
        </div>
        <div style={{ marginTop: '3rem', padding: '2.5rem', background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)', textAlign: 'center' }}>
          <h3 style={{ fontSize: '1.8rem', marginBottom: '1.5rem', color: 'var(--text)' }}>Por que escolher a Think TARS?</h3>
          <p style={{ fontSize: '1.25rem', lineHeight: '1.8', color: 'var(--text-muted)', maxWidth: '800px', margin: '0 auto' }}>
            Somos especialistas em criar soluções de automação e IA que resolvem problemas reais do seu negócio. Não vendemos tecnologia pelo simples fato de ser tecnologia — desenvolvemos soluções que geram valor mensurável, economizam tempo e aumentam a produtividade da sua equipe.
          </p>
        </div>
      </section>

      {/* Seção Soluções — Carrossel de Soluções */}
      <section id="solucoes" className="section">
        <h2 className="section-title">Soluções Eficientes</h2>
        <p className="section-subtitle">Porque acreditamos que automatizar é a única forma de não afundar no tempo</p>

        <div className="solutions-carousel-container">
          <div className="solutions-carousel-wrapper">
            <button 
              className="solutions-carousel-button solutions-carousel-button-prev" 
              onClick={prevSlide}
              aria-label="Slide anterior"
            >
              ‹
            </button>
            
            <div className="solutions-carousel-slides" style={{ transform: `translateX(-${currentSlide * 100}%)` }}>
              {solutions.map((solution, index) => (
                <div 
                  key={index} 
                  className="solutions-carousel-slide"
                  style={solution.backgroundImage ? {
                    backgroundImage: `url(${solution.backgroundImage})`,
                    backgroundSize: 'cover',
                    backgroundPosition: 'center',
                    backgroundRepeat: 'no-repeat'
                  } : {}}
                >
                  <div className="solution-card">
                    <div className="solution-icon">{solution.icon}</div>
                    <div className="solution-subtitle">{solution.subtitle}</div>
                    <h3 className="solution-title">{solution.title}</h3>
                    <p className="solution-description">{solution.description}</p>
                    <div className="solution-benefit">
                      <span className="benefit-badge">💰</span>
                      <span>{solution.benefit}</span>
          </div>
                    <a 
                      href="#contato" 
                      className="solution-cta"
                      onClick={(e) => { e.preventDefault(); scrollTo('contato') }}
                    >
                      Quero esta solução →
                    </a>
          </div>
          </div>
              ))}
          </div>

            <button 
              className="solutions-carousel-button solutions-carousel-button-next" 
              onClick={nextSlide}
              aria-label="Próximo slide"
            >
              ›
            </button>
        </div>

          <div className="solutions-carousel-indicators">
            {solutions.map((_, index) => (
              <button
                key={index}
                className={`solutions-carousel-indicator ${index === currentSlide ? 'active' : ''}`}
                onClick={() => goToSlide(index)}
                aria-label={`Ir para slide ${index + 1}`}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Seção Integrações */}
      <section id="integracoes" className="section" style={{ padding: '6rem 1.5rem', background: 'var(--bg-elevated)' }}>
        <div style={{ textAlign: 'center', marginBottom: '4rem', maxWidth: '1200px', margin: '0 auto 4rem' }}>
          <div style={{ display: 'inline-block', padding: '0.5rem 1.5rem', background: 'var(--accent-dim)', border: '1px solid var(--accent)', borderRadius: 999, marginBottom: '1.5rem', fontSize: '1.1rem', fontWeight: 600, color: 'var(--accent)', letterSpacing: '0.05em' }}>
            🔗 INTEGRAÇÕES PERSONALIZADAS
          </div>
          <h2 className="section-title" style={{ fontSize: '3rem', marginBottom: '1.5rem', background: 'linear-gradient(135deg, var(--text) 0%, var(--accent) 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
            IA Integrada ao Seu Sistema
          </h2>
          <p className="section-subtitle" style={{ fontSize: '1.4rem', lineHeight: '1.8', maxWidth: '800px', margin: '0 auto' }}>
            Não importa qual sistema você usa. Integramos IA personalizada diretamente no seu ERP, CRM, ferramentas do Google, WhatsApp e muito mais.
          </p>
        </div>

        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2rem', marginBottom: '3rem' }}>
            {/* ERP */}
            <div style={{ 
              padding: '2.5rem', 
              background: 'var(--surface)', 
              borderRadius: 20, 
              border: '2px solid var(--border)',
              textAlign: 'center',
              transition: 'all 0.3s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent)'
              e.currentTarget.style.transform = 'translateY(-8px)'
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 107, 53, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
            >
              <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>📊</div>
              <h3 style={{ fontSize: '1.8rem', marginBottom: '1rem', color: 'var(--text)' }}>ERP</h3>
              <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', lineHeight: '1.7', margin: 0 }}>
                Integramos IA no seu ERP para automatizar processos, gerar relatórios inteligentes e otimizar operações.
              </p>
            </div>

            {/* CRM */}
            <div style={{ 
              padding: '2.5rem', 
              background: 'var(--surface)', 
              borderRadius: 20, 
              border: '2px solid var(--border)',
              textAlign: 'center',
              transition: 'all 0.3s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent)'
              e.currentTarget.style.transform = 'translateY(-8px)'
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 107, 53, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
            >
              <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>👥</div>
              <h3 style={{ fontSize: '1.8rem', marginBottom: '1rem', color: 'var(--text)' }}>CRM</h3>
              <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', lineHeight: '1.7', margin: 0 }}>
                IA integrada ao seu CRM para qualificar leads, prever vendas e personalizar atendimento automaticamente.
              </p>
            </div>

            {/* Google Workspace */}
            <div style={{ 
              padding: '2.5rem', 
              background: 'var(--surface)', 
              borderRadius: 20, 
              border: '2px solid var(--border)',
              textAlign: 'center',
              transition: 'all 0.3s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent)'
              e.currentTarget.style.transform = 'translateY(-8px)'
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 107, 53, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
            >
              <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>🔷</div>
              <h3 style={{ fontSize: '1.8rem', marginBottom: '1rem', color: 'var(--text)' }}>Google Workspace</h3>
              <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', lineHeight: '1.7', margin: 0 }}>
                Automações inteligentes no Google Sheets, Gmail, Drive e Calendar para aumentar sua produtividade.
              </p>
            </div>

            {/* WhatsApp */}
            <div style={{ 
              padding: '2.5rem', 
              background: 'var(--surface)', 
              borderRadius: 20, 
              border: '2px solid var(--border)',
              textAlign: 'center',
              transition: 'all 0.3s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent)'
              e.currentTarget.style.transform = 'translateY(-8px)'
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 107, 53, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
            >
              <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>💬</div>
              <h3 style={{ fontSize: '1.8rem', marginBottom: '1rem', color: 'var(--text)' }}>WhatsApp</h3>
              <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', lineHeight: '1.7', margin: 0 }}>
                Assistentes de IA no WhatsApp para atendimento 24/7, qualificação de leads e vendas automatizadas.
              </p>
            </div>
          </div>

          {/* Destaque Personalização */}
          <div style={{ 
            padding: '3rem', 
            background: 'linear-gradient(135deg, var(--accent-dim) 0%, rgba(255, 107, 53, 0.1) 100%)', 
            borderRadius: 20, 
            border: '2px solid var(--accent)',
            textAlign: 'center'
          }}>
            <h3 style={{ fontSize: '2rem', marginBottom: '1rem', color: 'var(--text)' }}>
              Tudo Personalizado para Sua Empresa
            </h3>
            <p style={{ fontSize: '1.3rem', color: 'var(--text-muted)', marginBottom: '2rem', lineHeight: '1.8', maxWidth: '900px', margin: '0 auto 2rem' }}>
              Não vendemos soluções prontas. Desenvolvemos IA e automações sob medida para o seu negócio, 
              integrando perfeitamente com os sistemas que você já usa. Cada projeto é único e pensado para 
              resolver os desafios específicos da sua empresa.
            </p>
            <a 
              href="#contato" 
              className="hero-cta"
              onClick={(e) => { e.preventDefault(); scrollTo('contato') }}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '1.25rem 3rem',
                background: 'var(--accent)',
                color: 'var(--bg)',
                textDecoration: 'none',
                fontWeight: 700,
                fontSize: '1.3rem',
                borderRadius: 16,
                transition: 'all 0.3s',
                boxShadow: '0 8px 24px rgba(255, 107, 53, 0.4)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px) scale(1.05)'
                e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 107, 53, 0.6)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0) scale(1)'
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(255, 107, 53, 0.4)'
              }}
            >
              Quero Integrar IA no Meu Sistema →
            </a>
          </div>
        </div>
      </section>

      {/* Seção Playground — Assistentes de IA */}
      <section id="playground" className="section" style={{ padding: '6rem 1.5rem', background: 'linear-gradient(180deg, var(--bg) 0%, var(--bg-elevated) 100%)' }}>
        <div style={{ textAlign: 'center', marginBottom: '4rem', maxWidth: '1200px', margin: '0 auto 4rem' }}>
          <div style={{ display: 'inline-block', padding: '0.5rem 1.5rem', background: 'var(--accent-dim)', border: '1px solid var(--accent)', borderRadius: 999, marginBottom: '1.5rem', fontSize: '1.1rem', fontWeight: 600, color: 'var(--accent)', letterSpacing: '0.05em' }}>
            🤖 EXPERIMENTE AGORA
          </div>
          <h2 className="section-title" style={{ fontSize: '3rem', marginBottom: '1.5rem', background: 'linear-gradient(135deg, var(--text) 0%, var(--accent) 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
            Playground de Assistentes de IA
          </h2>
          <p className="section-subtitle" style={{ fontSize: '1.4rem', lineHeight: '1.8', marginBottom: '2.5rem' }}>
            Imagine ter acesso a especialistas de IA que trabalham 24/7, sem férias, sem pausas, sempre prontos para ajudar. Agora você pode experimentar isso agora mesmo.
          </p>
        </div>

        {/* Storytelling */}
        <div style={{ maxWidth: '1300px', margin: '0 auto 4rem', padding: '3rem', background: 'var(--surface)', borderRadius: 20, border: '1px solid var(--border)', boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '2.5rem', marginBottom: '3rem' }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>⚡</div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '0.75rem', color: 'var(--accent)' }}>Respostas Instantâneas</h3>
              <p style={{ fontSize: '1.15rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
                Pergunte qualquer coisa e receba respostas precisas em segundos, não em horas ou dias.
              </p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>📚</div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '0.75rem', color: 'var(--accent)' }}>Conhecimento Personalizado</h3>
              <p style={{ fontSize: '1.15rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
                Envie seus documentos e transforme o assistente em um especialista no seu conteúdo.
              </p>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: '3.5rem', marginBottom: '1rem' }}>🎯</div>
              <h3 style={{ fontSize: '1.5rem', marginBottom: '0.75rem', color: 'var(--accent)' }}>Múltiplos Especialistas</h3>
              <p style={{ fontSize: '1.15rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
                Teste diferentes assistentes: jurídico, investimentos, marketing, RH, vendas, suporte técnico, redação e muito mais.
              </p>
            </div>
          </div>
          
          <div style={{ padding: '2rem', background: 'var(--bg)', borderRadius: 12, border: '2px solid var(--accent)', textAlign: 'center' }}>
            <p style={{ fontSize: '1.3rem', lineHeight: '1.8', color: 'var(--text)', margin: 0 }}>
              <strong style={{ color: 'var(--accent)' }}>Não precisa de cadastro, não precisa de cartão de crédito.</strong><br />
              Simplesmente escolha um assistente, faça sua pergunta e veja a mágica acontecer. É assim que o futuro do trabalho se parece.
            </p>
          </div>
        </div>

        {/* Destaque dos Assistentes — Carrossel */}
        <div style={{ marginBottom: '3rem', textAlign: 'center' }}>
          <h3 style={{ fontSize: '2rem', marginBottom: '1.5rem', color: 'var(--text)' }}>Escolha seu Assistente Especializado</h3>
          
          <div className="agents-carousel-container" style={{ maxWidth: '1000px', margin: '0 auto', position: 'relative' }}>
            <div className="agents-carousel-wrapper">
              <button 
                className="agents-carousel-button agents-carousel-button-prev" 
                onClick={prevAgentSlide}
                aria-label="Assistente anterior"
              >
                ‹
              </button>
              
              <div className="agents-carousel-slides" style={{ 
                transform: `translateX(-${currentAgentSlide * 100}%)`
              }}>
                {Array.from({ length: Math.ceil(assistants.length / 4) }).map((_, slideIndex) => (
                  <div key={slideIndex} style={{ minWidth: '100%', display: 'flex', gap: '0.75rem', padding: '0.5rem', justifyContent: 'center', alignItems: 'stretch', height: 'auto' }}>
                    {assistants.slice(slideIndex * 4, slideIndex * 4 + 4).map((assistant) => (
                      <div
                        key={assistant.id}
                        onClick={() => {
                          setSelected(assistant.id)
                  setConversationId(null)
                  setMessages([])
                  setPdfFile(null)
                  if (fileInputRef.current) fileInputRef.current.value = ''
                }}
                style={{
                          flex: '1 1 0',
                          minWidth: 0,
                          padding: '0.6rem 0.5rem',
                          background: selected === assistant.id ? 'var(--accent-dim)' : 'var(--surface)',
                          border: `2px solid ${selected === assistant.id ? 'var(--accent)' : 'var(--border)'}`,
                          borderRadius: 10,
                          cursor: 'pointer',
                          transition: 'all 0.3s',
                          transform: selected === assistant.id ? 'translateY(-4px)' : 'none',
                          boxShadow: selected === assistant.id ? '0 8px 24px rgba(255, 107, 53, 0.3)' : 'none',
                          textAlign: 'center',
                          display: 'flex',
                          flexDirection: 'column',
                          alignItems: 'center',
                          justifyContent: 'flex-start',
                          height: 'auto'
                        }}
                        onMouseEnter={(e) => {
                          if (selected !== assistant.id) {
                            e.currentTarget.style.borderColor = 'var(--accent)'
                            e.currentTarget.style.transform = 'translateY(-2px)'
                          }
                        }}
                        onMouseLeave={(e) => {
                          if (selected !== assistant.id) {
                            e.currentTarget.style.borderColor = 'var(--border)'
                            e.currentTarget.style.transform = 'translateY(0)'
                          }
                        }}
                      >
                        <div style={{ fontSize: '1.75rem', marginBottom: '0.4rem' }}>
                          {assistant.id === 'juridico' ? '⚖️' : 
                           assistant.id === 'investment' ? '📊' : 
                           assistant.id === 'planilha' ? '📈' : 
                           assistant.id === 'marketing' ? '📱' : 
                           assistant.id === 'rh' ? '👥' : 
                           assistant.id === 'suporte' ? '🔧' : 
                           assistant.id === 'vendas' ? '💰' : 
                           assistant.id === 'redacao' ? '✍️' : 
                           '🤖'}
                        </div>
                        <h4 style={{ fontSize: '0.9rem', marginBottom: '0.2rem', color: 'var(--text)', fontWeight: 600, lineHeight: '1.2' }}>
                          {assistant.name}
                        </h4>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', margin: 0, lineHeight: '1.3' }}>
                          {assistant.id === 'juridico' ? 'Análise jurídica' : 
                           assistant.id === 'investment' ? 'Análise de investimentos' : 
                           assistant.id === 'planilha' ? 'Análise de dados' : 
                           assistant.id === 'marketing' ? 'Marketing digital' : 
                           assistant.id === 'rh' ? 'Recursos humanos' : 
                           assistant.id === 'suporte' ? 'Suporte técnico' : 
                           assistant.id === 'vendas' ? 'Vendas e negociação' : 
                           assistant.id === 'redacao' ? 'Redação e conteúdo' : 
                           'Assistente especializado'}
                        </p>
                      </div>
                    ))}
                  </div>
                ))}
              </div>

                      <button
                className="agents-carousel-button agents-carousel-button-next" 
                onClick={nextAgentSlide}
                aria-label="Próximo assistente"
              >
                ›
                      </button>
                    </div>

            <div className="agents-carousel-indicators">
              {Array.from({ length: Math.ceil(assistants.length / 4) }).map((_, index) => (
                <button
                  key={index}
                  className={`agents-carousel-indicator ${index === currentAgentSlide ? 'active' : ''}`}
                  onClick={() => goToAgentSlide(index)}
                  aria-label={`Ir para slide ${index + 1}`}
                />
              ))}
            </div>
          </div>
        </div>

        {/* Área do chat (Playground) */}
        <div id="playground-chat" className="demos-wrapper" style={{ height: '700px', border: '2px solid var(--accent)', boxShadow: '0 12px 48px rgba(255, 107, 53, 0.2)', borderRadius: '16px', overflow: 'hidden', position: 'relative', display: 'flex', flexDirection: 'column' }}>
          <div className="chat-main chat-layout" style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            {!conversationId ? (
              <div style={{ 
                flex: 1, 
                display: 'flex', 
                flexDirection: 'column', 
                alignItems: 'center', 
                justifyContent: 'center', 
                gap: '2rem', 
                      color: 'var(--text)',
                padding: '4rem 2rem', 
                textAlign: 'center',
                position: 'relative',
                background: 'linear-gradient(135deg, var(--bg-elevated) 0%, var(--surface) 100%)'
              }}>
                {/* Overlay escurecido */}
                <div style={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  bottom: 0,
                  background: 'rgba(0, 0, 0, 0.4)',
                  backdropFilter: 'blur(4px)',
                  zIndex: 1
                }} />
                
                {/* Conteúdo centralizado */}
                <div style={{ position: 'relative', zIndex: 2 }}>
                  <div style={{ fontSize: '5rem', marginBottom: '1.5rem' }}>🚀</div>
                  <h3 style={{ fontSize: '2rem', marginBottom: '1rem', color: 'var(--text)' }}>Pronto para começar?</h3>
                  <p style={{ fontSize: '1.4rem', color: 'var(--text-muted)', marginBottom: '2rem', maxWidth: '600px', lineHeight: '1.8' }}>
                    Você está prestes a conversar com <strong style={{ color: 'var(--accent)' }}>{currentName}</strong>. 
                    Clique no botão abaixo para iniciar a conversa e experimentar o poder da IA.
                  </p>

              <button
                type="button"
                onClick={startConversation}
                disabled={loading || !selected}
                style={{
                      padding: '1.25rem 3rem',
                  background: 'var(--accent)',
                  border: 'none',
                      borderRadius: 16,
                  color: 'var(--bg)',
                  fontFamily: 'var(--font-sans)',
                      fontSize: '1.4rem',
                      fontWeight: 700,
                  cursor: loading || !selected ? 'not-allowed' : 'pointer',
                      transition: 'all 0.3s',
                      boxShadow: loading || !selected ? 'none' : '0 8px 24px rgba(255, 107, 53, 0.5)',
                      opacity: loading || !selected ? 0.6 : 1,
                      position: 'relative',
                      zIndex: 3
                    }}
                    onMouseEnter={(e) => {
                      if (!loading && selected) {
                        e.currentTarget.style.transform = 'translateY(-4px) scale(1.05)'
                        e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 107, 53, 0.6)'
                      }
                    }}
                    onMouseLeave={(e) => {
                      if (!loading && selected) {
                        e.currentTarget.style.transform = 'translateY(0) scale(1)'
                        e.currentTarget.style.boxShadow = '0 8px 24px rgba(255, 107, 53, 0.5)'
                      }
                    }}
                  >
                    {loading ? '⏳ Processando...' : '🚀 Iniciar Conversa'}
              </button>
                </div>
              </div>
              ) : (
                <>
                  {/* Header do chat com botão para nova conversa */}
                  <div style={{ padding: '1rem 1.5rem', borderBottom: '1px solid var(--border)', background: 'var(--surface)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h4 style={{ fontSize: '1.3rem', margin: 0, color: 'var(--text)' }}>{currentName}</h4>
                      {pdfFile && (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginTop: '0.25rem' }}>
                          <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                            {pdfFile.name.toLowerCase().endsWith('.pdf') ? '📄' : 
                             pdfFile.name.toLowerCase().endsWith('.xlsx') || pdfFile.name.toLowerCase().endsWith('.xls') ? '📊' :
                             pdfFile.name.toLowerCase().endsWith('.doc') || pdfFile.name.toLowerCase().endsWith('.docx') ? '📝' :
                             pdfFile.name.toLowerCase().endsWith('.txt') ? '📋' : '📎'} {pdfFile.name}
                          </span>
                          <button
                            type="button"
                            onClick={() => { setPdfFile(null); if (fileInputRef.current) fileInputRef.current.value = '' }}
                            style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '1rem', cursor: 'pointer', padding: '0 0.25rem' }}
                            title="Remover arquivo"
                          >
                            ×
                          </button>
                        </div>
                      )}
                    </div>
                <button
                  type="button"
                  onClick={() => { setConversationId(null); setMessages([]); setPdfFile(null); if (fileInputRef.current) fileInputRef.current.value = '' }}
                  style={{
                        padding: '0.5rem 1rem',
                    background: 'transparent',
                    border: '1px solid var(--border)',
                        borderRadius: 8,
                    color: 'var(--text-muted)',
                    fontFamily: 'var(--font-sans)',
                        fontSize: '1rem',
                    cursor: 'pointer',
                  }}
                >
                      🔄 Nova Conversa
                </button>
                </div>

                  <div className="chat-messages" style={{ flex: 1, overflowY: 'auto', overflowX: 'hidden', padding: '1.5rem', minHeight: 0 }}>
                    {messages.map((msg, i) => (
                      <div
                        key={i}
                        style={{
                          maxWidth: '85%',
                          padding: '0.75rem 1rem',
                          borderRadius: 12,
                          alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                          background: msg.role === 'user' ? 'var(--accent-dim)' : 'var(--surface)',
                          border: `1px solid ${msg.role === 'user' ? 'var(--accent)' : 'var(--border)'}`,
                          marginBottom: '1rem',
                          ...(msg.isError && { borderColor: 'var(--error)', color: 'var(--error)' }),
                        }}
                      >
                        <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.25rem' }}>
                          {msg.role === 'user' ? 'Você' : currentName}
                        </span>
                        {msg.file && (
                          <div style={{ fontSize: '0.85rem', color: msg.role === 'user' ? 'rgba(255,255,255,0.9)' : 'var(--accent)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            📎 {msg.file}
                          </div>
                        )}
                        <div style={{ fontSize: '1.15rem', wordBreak: 'break-word' }} className="markdown-content">
                          {msg.role === 'assistant' ? (
                            <ReactMarkdown>{msg.content}</ReactMarkdown>
                          ) : (
                            <div style={{ whiteSpace: 'pre-wrap' }}>{msg.content}</div>
                          )}
                        </div>
                      </div>
                    ))}
                    {loading && (
                      <div style={{ maxWidth: '85%', padding: '0.75rem 1rem', borderRadius: 12, alignSelf: 'flex-start', background: 'var(--surface)', border: '1px solid var(--border)', marginBottom: '1rem' }}>
                        <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)' }}>{currentName}</span>
                        <div style={{ fontSize: '1.15rem' }}>...</div>
                      </div>
                    )}
                    {uploadProgress && (
                      <div style={{ padding: '1rem', background: 'var(--accent-dim)', border: '1px solid var(--accent)', borderRadius: 8, marginBottom: '1rem', textAlign: 'center' }}>
                        <div style={{ fontSize: '1.05rem', color: 'var(--accent)' }}>{uploadProgress}</div>
                      </div>
                    )}
                    <div ref={bottomRef} />
                  </div>
                  <div className="chat-input-row" style={{ padding: '1rem 1.5rem', borderTop: '1px solid var(--border)', background: 'var(--surface)', display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
                    {/* Botão de anexo para arquivos */}
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept="*/*"
                      onChange={handleFileSelect}
                      style={{ display: 'none' }}
                      id="file-upload-input"
                      disabled={loading}
                    />
                    <button
                      type="button"
                      onClick={() => {
                        if (fileInputRef.current) {
                          fileInputRef.current.click()
                        }
                      }}
                      disabled={loading}
                      style={{
                        padding: '0.75rem',
                        background: 'var(--bg)',
                        border: '1px solid var(--border)',
                        borderRadius: 8,
                        color: 'var(--text)',
                        cursor: loading ? 'not-allowed' : 'pointer',
                        fontSize: '1.5rem',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        minWidth: '48px',
                        width: '48px',
                        height: '48px',
                        transition: 'all 0.2s',
                        opacity: loading ? 0.5 : 1,
                        flexShrink: 0
                      }}
                      title="Anexar arquivo"
                      onMouseEnter={(e) => {
                        if (!loading) {
                          e.currentTarget.style.background = 'var(--accent-dim)'
                          e.currentTarget.style.borderColor = 'var(--accent)'
                          e.currentTarget.style.transform = 'scale(1.1)'
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!loading) {
                          e.currentTarget.style.background = 'var(--bg)'
                          e.currentTarget.style.borderColor = 'var(--border)'
                          e.currentTarget.style.transform = 'scale(1)'
                        }
                      }}
                    >
                      📎
                    </button>
                    {pdfFile && (
                      <div style={{ 
                        display: 'flex', 
                        alignItems: 'center', 
                        gap: '0.5rem', 
                        padding: '0.5rem 0.75rem', 
                        background: 'var(--accent-dim)', 
                        border: '1px solid var(--accent)', 
                        borderRadius: 8,
                        fontSize: '0.9rem',
                        color: 'var(--accent)',
                        maxWidth: '250px',
                        height: '48px',
                        boxSizing: 'border-box'
                      }}>
                        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                          {pdfFile.name.toLowerCase().endsWith('.pdf') ? '📄' : 
                           pdfFile.name.toLowerCase().endsWith('.xlsx') || pdfFile.name.toLowerCase().endsWith('.xls') ? '📊' :
                           pdfFile.name.toLowerCase().endsWith('.doc') || pdfFile.name.toLowerCase().endsWith('.docx') ? '📝' :
                           pdfFile.name.toLowerCase().endsWith('.txt') ? '📋' : '📎'} {pdfFile.name}
                        </span>
                        <button
                          type="button"
                          onClick={() => { setPdfFile(null); if (fileInputRef.current) fileInputRef.current.value = '' }}
                          style={{ background: 'none', border: 'none', color: 'var(--accent)', fontSize: '1rem', cursor: 'pointer', padding: '0 0.25rem', flexShrink: 0 }}
                          title="Remover arquivo"
                        >
                          ×
                        </button>
                      </div>
                    )}
                    <textarea
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Digite sua mensagem..."
                      rows={2}
                      style={{
                        flex: 1,
                        padding: '0.75rem 1rem',
                        background: 'var(--bg)',
                        border: '1px solid var(--border)',
                        borderRadius: 8,
                        color: 'var(--text)',
                        fontFamily: 'var(--font-sans)',
                        fontSize: '1.15rem',
                        resize: 'none',
                        height: '48px',
                        minHeight: '48px',
                        maxHeight: '48px',
                        lineHeight: '1.5',
                        boxSizing: 'border-box',
                        overflow: 'hidden'
                      }}
                      disabled={loading}
                    />
                    <button
                      type="button"
                      onClick={sendMessage}
                      disabled={loading || !input.trim()}
                      style={{
                        padding: '0.75rem 1.5rem',
                        background: 'var(--accent)',
                        border: 'none',
                        borderRadius: 8,
                        color: 'var(--bg)',
                        fontFamily: 'var(--font-sans)',
                        fontSize: '1.15rem',
                        fontWeight: 600,
                        cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
                        minWidth: '100px',
                        height: '48px',
                        opacity: loading || !input.trim() ? 0.6 : 1,
                        transition: 'all 0.2s',
                        flexShrink: 0,
                        boxSizing: 'border-box'
                      }}
                      onMouseEnter={(e) => {
                        if (!loading && input.trim()) {
                          e.currentTarget.style.transform = 'translateY(-1px)'
                          e.currentTarget.style.boxShadow = '0 4px 12px rgba(255, 107, 53, 0.4)'
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!loading && input.trim()) {
                          e.currentTarget.style.transform = 'translateY(0)'
                          e.currentTarget.style.boxShadow = 'none'
                        }
                      }}
                    >
                      Enviar
                    </button>
                  </div>
                </>
              )}
            </div>
        </div>
      </section>

      {/* Seção Próximas Etapas */}
      <section id="proximas-etapas" className="section" style={{ padding: '6rem 1.5rem', background: 'linear-gradient(180deg, var(--bg-elevated) 0%, var(--bg) 100%)' }}>
        <div style={{ textAlign: 'center', marginBottom: '4rem', maxWidth: '1200px', margin: '0 auto 4rem' }}>
          <div style={{ display: 'inline-block', padding: '0.5rem 1.5rem', background: 'var(--accent-dim)', border: '1px solid var(--accent)', borderRadius: 999, marginBottom: '1.5rem', fontSize: '1.1rem', fontWeight: 600, color: 'var(--accent)', letterSpacing: '0.05em' }}>
            🚀 COMO FUNCIONA
          </div>
          <h2 className="section-title" style={{ fontSize: '3rem', marginBottom: '1.5rem', background: 'linear-gradient(135deg, var(--text) 0%, var(--accent) 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
            Do Sonho à Realidade em 4 Passos
          </h2>
          <p className="section-subtitle" style={{ fontSize: '1.4rem', lineHeight: '1.8', maxWidth: '800px', margin: '0 auto' }}>
            Transformamos sua ideia em uma solução de IA que funciona. Veja como é simples e rápido.
          </p>
        </div>

        <div style={{ maxWidth: '1300px', margin: '0 auto', position: 'relative' }}>
          {/* Linha conectora - visível apenas em telas grandes */}
          <div style={{ 
            position: 'absolute', 
            top: '120px', 
            left: '10%', 
            right: '10%', 
            height: '3px', 
            background: 'linear-gradient(90deg, var(--accent) 0%, var(--accent-hover) 100%)',
            zIndex: 0,
            borderRadius: '2px',
            display: 'none'
          }} 
          className="timeline-connector"
          />

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '2.5rem', position: 'relative', zIndex: 1 }}>
            {/* Etapa 1 */}
            <div style={{ 
              padding: '2.5rem', 
              background: 'var(--surface)', 
              borderRadius: 20, 
              border: '2px solid var(--border)',
              textAlign: 'center',
              transition: 'all 0.3s',
              position: 'relative'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent)'
              e.currentTarget.style.transform = 'translateY(-8px)'
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 107, 53, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
            >
              <div style={{ 
                width: '80px', 
                height: '80px', 
                borderRadius: '50%', 
                background: 'var(--accent-dim)', 
                border: '3px solid var(--accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '2.5rem',
                margin: '0 auto 1.5rem',
                fontWeight: 'bold',
                color: 'var(--accent)'
              }}>
                1
              </div>
              <h3 style={{ fontSize: '1.8rem', marginBottom: '1rem', color: 'var(--text)' }}>Fale com um Especialista</h3>
              <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', lineHeight: '1.7', margin: 0 }}>
                Conte sua ideia ou use nosso quiz para estruturar seu projeto. Nossa equipe entende suas necessidades e desafios.
              </p>
            </div>

            {/* Etapa 2 */}
            <div style={{ 
              padding: '2.5rem', 
              background: 'var(--surface)', 
              borderRadius: 20, 
              border: '2px solid var(--border)',
              textAlign: 'center',
              transition: 'all 0.3s',
              position: 'relative'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent)'
              e.currentTarget.style.transform = 'translateY(-8px)'
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 107, 53, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
            >
              <div style={{ 
                width: '80px', 
                height: '80px', 
                borderRadius: '50%', 
                background: 'var(--accent-dim)', 
                border: '3px solid var(--accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '2.5rem',
                margin: '0 auto 1.5rem',
                fontWeight: 'bold',
                color: 'var(--accent)'
              }}>
                2
              </div>
              <h3 style={{ fontSize: '1.8rem', marginBottom: '1rem', color: 'var(--text)' }}>Aprove o Projeto</h3>
              <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', lineHeight: '1.7', margin: 0 }}>
                Nossos especialistas elaboram um escopo detalhado. Você revisa, aprova e damos início ao desenvolvimento.
              </p>
            </div>

            {/* Etapa 3 */}
            <div style={{ 
              padding: '2.5rem', 
              background: 'var(--surface)', 
              borderRadius: 20, 
              border: '2px solid var(--border)',
              textAlign: 'center',
              transition: 'all 0.3s',
              position: 'relative'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent)'
              e.currentTarget.style.transform = 'translateY(-8px)'
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 107, 53, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
            >
              <div style={{ 
                width: '80px', 
                height: '80px', 
                borderRadius: '50%', 
                background: 'var(--accent-dim)', 
                border: '3px solid var(--accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '2.5rem',
                margin: '0 auto 1.5rem',
                fontWeight: 'bold',
                color: 'var(--accent)'
              }}>
                3
              </div>
              <h3 style={{ fontSize: '1.8rem', marginBottom: '1rem', color: 'var(--text)' }}>Acompanhe o Desenvolvimento</h3>
              <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', lineHeight: '1.7', margin: 0 }}>
                Fique por dentro de cada etapa. Você recebe atualizações regulares e pode testar a solução durante o desenvolvimento.
              </p>
            </div>

            {/* Etapa 4 */}
            <div style={{ 
              padding: '2.5rem', 
              background: 'var(--surface)', 
              borderRadius: 20, 
              border: '2px solid var(--border)',
              textAlign: 'center',
              transition: 'all 0.3s',
              position: 'relative'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.borderColor = 'var(--accent)'
              e.currentTarget.style.transform = 'translateY(-8px)'
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 107, 53, 0.3)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.borderColor = 'var(--border)'
              e.currentTarget.style.transform = 'translateY(0)'
              e.currentTarget.style.boxShadow = 'none'
            }}
            >
              <div style={{ 
                width: '80px', 
                height: '80px', 
                borderRadius: '50%', 
                background: 'var(--accent-dim)', 
                border: '3px solid var(--accent)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '2.5rem',
                margin: '0 auto 1.5rem',
                fontWeight: 'bold',
                color: 'var(--accent)'
              }}>
                4
              </div>
              <h3 style={{ fontSize: '1.8rem', marginBottom: '1rem', color: 'var(--text)' }}>Veja os Resultados</h3>
              <p style={{ fontSize: '1.2rem', color: 'var(--text-muted)', lineHeight: '1.7', margin: 0 }}>
                Sua solução entra em produção e você acompanha os resultados em tempo real. Economia de tempo e aumento de produtividade garantidos.
              </p>
            </div>
          </div>

          {/* CTA Final */}
          <div style={{ 
            marginTop: '4rem', 
            padding: '3rem', 
            background: 'linear-gradient(135deg, var(--accent-dim) 0%, rgba(255, 107, 53, 0.1) 100%)', 
            borderRadius: 20, 
            border: '2px solid var(--accent)',
            textAlign: 'center'
          }}>
            <h3 style={{ fontSize: '2rem', marginBottom: '1rem', color: 'var(--text)' }}>
              Pronto para começar?
            </h3>
            <p style={{ fontSize: '1.3rem', color: 'var(--text-muted)', marginBottom: '2rem', lineHeight: '1.8' }}>
              Não perca mais tempo com processos manuais. Transforme sua ideia em realidade hoje mesmo.
            </p>
            <a 
              href="#contato" 
              className="hero-cta"
              onClick={(e) => { e.preventDefault(); scrollTo('contato') }}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '1.25rem 3rem',
                background: 'var(--accent)',
                color: 'var(--bg)',
                textDecoration: 'none',
                fontWeight: 700,
                fontSize: '1.3rem',
                borderRadius: 16,
                transition: 'all 0.3s',
                boxShadow: '0 8px 24px rgba(255, 107, 53, 0.4)'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px) scale(1.05)'
                e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 107, 53, 0.6)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0) scale(1)'
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(255, 107, 53, 0.4)'
              }}
            >
              Começar Agora →
            </a>
          </div>
        </div>
      </section>

      {/* Seção FAQ */}
      <section id="faq" className="section" style={{ padding: '6rem 1.5rem', background: 'var(--bg)' }}>
        <div style={{ textAlign: 'center', marginBottom: '4rem', maxWidth: '1200px', margin: '0 auto 4rem' }}>
          <div style={{ display: 'inline-block', padding: '0.5rem 1.5rem', background: 'var(--accent-dim)', border: '1px solid var(--accent)', borderRadius: 999, marginBottom: '1.5rem', fontSize: '1.1rem', fontWeight: 600, color: 'var(--accent)', letterSpacing: '0.05em' }}>
            ❓ PERGUNTAS FREQUENTES
          </div>
          <h2 className="section-title" style={{ fontSize: '3rem', marginBottom: '1.5rem', background: 'linear-gradient(135deg, var(--text) 0%, var(--accent) 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
            Tire Suas Dúvidas
          </h2>
          <p className="section-subtitle" style={{ fontSize: '1.4rem', lineHeight: '1.8', maxWidth: '800px', margin: '0 auto' }}>
            Respostas para as principais dúvidas sobre projetos de IA e automação
          </p>
        </div>

        <div style={{ maxWidth: '900px', margin: '0 auto' }}>
          {[
            {
              question: 'Quanto tempo leva para desenvolver uma solução de IA personalizada?',
              answer: 'O prazo varia conforme a complexidade do projeto. Soluções mais simples podem ficar prontas em 2-4 semanas, enquanto projetos mais complexos podem levar 2-3 meses. Durante o primeiro contato, elaboramos um escopo detalhado com prazos específicos para o seu projeto.'
            },
            {
              question: 'Preciso ter conhecimento técnico para usar as soluções de IA?',
              answer: 'Não! Todas as nossas soluções são desenvolvidas para serem intuitivas e fáceis de usar. Você e sua equipe recebem treinamento completo e documentação detalhada. Nosso objetivo é que você use a IA sem precisar entender como ela funciona tecnicamente.'
            },
            {
              question: 'Como funciona a integração com meus sistemas atuais?',
              answer: 'Integramos a IA diretamente nos sistemas que você já usa (ERP, CRM, Google Workspace, WhatsApp, etc.) através de APIs e conectores personalizados. Não é necessário trocar de sistema ou fazer grandes mudanças. A IA trabalha em conjunto com suas ferramentas atuais.'
            },
            {
              question: 'Quanto custa um projeto de IA e automação?',
              answer: 'Cada projeto é único e o investimento varia conforme a complexidade, escopo e integrações necessárias. Oferecemos propostas personalizadas após entender suas necessidades. Trabalhamos com diferentes faixas de investimento para atender empresas de todos os portes.'
            },
            {
              question: 'As soluções de IA funcionam mesmo se eu não tiver muitos dados?',
              answer: 'Sim! Mesmo com poucos dados iniciais, podemos desenvolver soluções eficazes. A IA pode trabalhar com dados históricos, aprender com o uso contínuo e até mesmo usar modelos pré-treinados adaptados para o seu negócio. Conforme você usa a solução, ela fica cada vez mais inteligente.'
            },
            {
              question: 'Vocês oferecem suporte após a entrega do projeto?',
              answer: 'Sim! Oferecemos suporte técnico, manutenção e atualizações. Também fazemos melhorias contínuas baseadas no uso real da solução. Você pode escolher entre planos de suporte mensais ou suporte sob demanda, conforme sua necessidade.'
            },
            {
              question: 'Posso testar antes de contratar?',
              answer: 'Sim! Oferecemos uma fase de prova de conceito (POC) onde desenvolvemos uma versão simplificada da solução para você validar antes do investimento completo. Isso permite que você veja os resultados práticos antes de decidir.'
            },
            {
              question: 'A IA vai substituir funcionários da minha empresa?',
              answer: 'Não! Nossa abordagem é de IA como assistente, não como substituto. As soluções automatizam tarefas repetitivas e demoradas, liberando sua equipe para focar em atividades estratégicas e criativas que geram mais valor. O resultado é aumento de produtividade, não redução de equipe.'
            },
            {
              question: 'Como garantem a segurança dos dados da minha empresa?',
              answer: 'Seguimos as melhores práticas de segurança: criptografia de dados, acesso restrito, conformidade com LGPD, e podemos trabalhar com infraestrutura própria do cliente quando necessário. Todos os dados são tratados com máxima confidencialidade e segurança.'
            },
            {
              question: 'Quais tipos de automação vocês desenvolvem?',
              answer: 'Desenvolvemos automações para: atendimento ao cliente (chatbots, WhatsApp), análise de documentos e contratos, processamento de planilhas e relatórios, qualificação e follow-up de leads, gestão de processos internos, análise preditiva de dados, e muito mais. Se você tem um processo repetitivo, podemos automatizá-lo.'
            }
          ].map((faq, index) => {
            const isOpen = openFaqIndex === index
            return (
              <div 
                key={index}
                style={{ 
                  marginBottom: '1.5rem',
                  background: 'var(--surface)',
                  borderRadius: 16,
                  border: `2px solid ${isOpen ? 'var(--accent)' : 'var(--border)'}`,
                  overflow: 'hidden',
                  transition: 'all 0.3s',
                  boxShadow: isOpen ? '0 4px 16px rgba(255, 107, 53, 0.15)' : 'none'
                }}
                onMouseEnter={(e) => {
                  if (!isOpen) {
                    e.currentTarget.style.borderColor = 'var(--accent)'
                    e.currentTarget.style.boxShadow = '0 4px 16px rgba(255, 107, 53, 0.1)'
                  }
                }}
                onMouseLeave={(e) => {
                  if (!isOpen) {
                    e.currentTarget.style.borderColor = 'var(--border)'
                    e.currentTarget.style.boxShadow = 'none'
                  }
                }}
              >
                <div 
                  style={{ 
                    padding: '1.5rem 2rem',
                    cursor: 'pointer',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: isOpen ? 'var(--accent-dim)' : 'var(--bg-elevated)',
                    transition: 'background 0.3s'
                  }}
                  onClick={() => setOpenFaqIndex(isOpen ? null : index)}
                >
                  <h3 style={{ fontSize: '1.3rem', fontWeight: 600, color: 'var(--text)', margin: 0, flex: 1 }}>
                    {faq.question}
                  </h3>
                  <span style={{ 
                    fontSize: '1.5rem', 
                    color: 'var(--accent)', 
                    transition: 'transform 0.3s',
                    marginLeft: '1rem',
                    flexShrink: 0,
                    transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)'
                  }}>
                    ▼
                  </span>
                </div>
                {isOpen && (
                  <div style={{ 
                    padding: '0 2rem 1.5rem 2rem',
                    fontSize: '1.15rem',
                    color: 'var(--text-muted)',
                    lineHeight: '1.7',
                    animation: 'fadeIn 0.3s ease'
                  }}>
                    {faq.answer}
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* CTA FAQ */}
        <div style={{ 
          marginTop: '4rem', 
          padding: '3rem', 
          background: 'linear-gradient(135deg, var(--accent-dim) 0%, rgba(255, 107, 53, 0.1) 100%)', 
          borderRadius: 20, 
          border: '2px solid var(--accent)',
          textAlign: 'center',
          maxWidth: '900px',
          margin: '4rem auto 0'
        }}>
          <h3 style={{ fontSize: '2rem', marginBottom: '1rem', color: 'var(--text)' }}>
            Ainda tem dúvidas?
          </h3>
          <p style={{ fontSize: '1.3rem', color: 'var(--text-muted)', marginBottom: '2rem', lineHeight: '1.8' }}>
            Fale diretamente com nossa equipe. Estamos prontos para esclarecer qualquer questão e ajudar você a encontrar a melhor solução para seu negócio.
          </p>
          <a 
            href="#contato" 
            className="hero-cta"
            onClick={(e) => { e.preventDefault(); scrollTo('contato') }}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '1.25rem 3rem',
              background: 'var(--accent)',
              color: 'var(--bg)',
              textDecoration: 'none',
              fontWeight: 700,
              fontSize: '1.3rem',
              borderRadius: 16,
              transition: 'all 0.3s',
              boxShadow: '0 8px 24px rgba(255, 107, 53, 0.4)'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'translateY(-4px) scale(1.05)'
              e.currentTarget.style.boxShadow = '0 12px 32px rgba(255, 107, 53, 0.6)'
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0) scale(1)'
              e.currentTarget.style.boxShadow = '0 8px 24px rgba(255, 107, 53, 0.4)'
            }}
          >
            Falar com Especialista →
          </a>
        </div>
      </section>

      {/* Seção Contato — Interativa */}
      <section id="contato" className="contact-section">
        <h2 className="section-title">Entre em Contato</h2>
        <p className="section-subtitle">Tem alguma ideia para o seu negócio? Vamos transformá-la em realidade!</p>

        {!contactMode ? (
          <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center', flexWrap: 'wrap', marginTop: '2rem' }}>
            <button
              onClick={() => setContactMode('has-idea')}
              style={{
                padding: '1.5rem 3rem',
                background: 'var(--accent)',
                border: 'none',
                borderRadius: 12,
                color: 'var(--bg)',
                fontSize: '1.3rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.15)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)' }}
            >
              💡 Já tenho uma ideia
            </button>
            <button
              onClick={() => setContactMode('needs-help')}
              style={{
                padding: '1.5rem 3rem',
                background: 'var(--surface)',
                border: '2px solid var(--accent)',
                borderRadius: 12,
                color: 'var(--accent)',
                fontSize: '1.3rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                boxShadow: '0 4px 12px rgba(0,0,0,0.1)'
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 6px 16px rgba(0,0,0,0.15)' }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)' }}
            >
              🤔 Preciso de ajuda para estruturar
            </button>
          </div>
        ) : contactMode === 'has-idea' ? (
          <div style={{ maxWidth: '800px', margin: '2rem auto', padding: '2rem', background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)' }}>
            <h3 style={{ marginBottom: '1.5rem', color: 'var(--text)', fontSize: '1.8rem' }}>Conte-nos sobre sua ideia</h3>
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text)', fontWeight: 500, fontSize: '1.15rem' }}>
                Seu nome *
              </label>
              <input
                type="text"
                value={contactName}
                onChange={(e) => setContactName(e.target.value)}
                placeholder="Digite seu nome"
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'var(--bg)',
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  color: 'var(--text)',
                  fontSize: '1.15rem',
                  fontFamily: 'var(--font-sans)'
                }}
              />
            </div>
            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', color: 'var(--text)', fontWeight: 500, fontSize: '1.15rem' }}>
                Descrição da sua ideia *
              </label>
              <textarea
                value={contactIdea}
                onChange={(e) => setContactIdea(e.target.value)}
                placeholder="Descreva sua ideia de projeto em detalhes..."
                rows={6}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  background: 'var(--bg)',
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  color: 'var(--text)',
                  fontSize: '1.15rem',
                  fontFamily: 'var(--font-sans)',
                  resize: 'vertical'
                }}
              />
            </div>
            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end' }}>
              <button
                onClick={() => {
                  setContactMode(null)
                  setContactName('')
                  setContactIdea('')
                }}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'transparent',
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  color: 'var(--text)',
                  cursor: 'pointer',
                  fontSize: '1rem'
                }}
              >
                Cancelar
              </button>
              <button
                onClick={handleSubmitIdea}
                disabled={!contactName.trim() || !contactIdea.trim()}
                style={{
                  padding: '0.75rem 1.5rem',
                  background: 'var(--accent)',
                  border: 'none',
                  borderRadius: 8,
                  color: 'var(--bg)',
                  cursor: !contactName.trim() || !contactIdea.trim() ? 'not-allowed' : 'pointer',
                  fontSize: '1rem',
                  fontWeight: 600,
                  opacity: !contactName.trim() || !contactIdea.trim() ? 0.6 : 1
                }}
              >
                Entrar em Contato
              </button>
            </div>
          </div>
        ) : (
          <div style={{ maxWidth: '900px', margin: '2rem auto', padding: '2rem', background: 'var(--surface)', borderRadius: 12, border: '1px solid var(--border)' }}>
            {!projectScope ? (
              <>
                <div style={{ marginBottom: '2rem', textAlign: 'center' }}>
                  <h3 style={{ marginBottom: '0.5rem', color: 'var(--text)', fontSize: '1.4rem' }}>
                    Pergunta {quizStep + 1} de {quizQuestions.length}
                  </h3>
                  <div style={{ width: '100%', height: '4px', background: 'var(--border)', borderRadius: 2, overflow: 'hidden' }}>
                    <div
                      style={{
                        width: `${((quizStep + 1) / quizQuestions.length) * 100}%`,
                        height: '100%',
                        background: 'var(--accent)',
                        transition: 'width 0.3s'
                      }}
                    />
                  </div>
                </div>
                <h3 style={{ marginBottom: '1.5rem', color: 'var(--text)', fontSize: '1.8rem' }}>
                  {quizQuestions[quizStep].question}
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {quizQuestions[quizStep].options.map((option, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleQuizAnswer(quizQuestions[quizStep].id, option)}
                      style={{
                        padding: '1rem 1.5rem',
                        background: 'var(--bg)',
                        border: '2px solid var(--border)',
                        borderRadius: 8,
                        color: 'var(--text)',
                        fontSize: '1.2rem',
                        textAlign: 'left',
                        cursor: 'pointer',
                        transition: 'all 0.2s',
                        fontWeight: 500
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = 'var(--accent)'
                        e.currentTarget.style.background = 'var(--accent)'
                        e.currentTarget.style.color = 'var(--bg)'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = 'var(--border)'
                        e.currentTarget.style.background = 'var(--bg)'
                        e.currentTarget.style.color = 'var(--text)'
                      }}
                    >
                      {option}
                    </button>
                  ))}
                </div>
                {quizStep > 0 && (
                  <button
                    onClick={() => setQuizStep(quizStep - 1)}
                    style={{
                      marginTop: '1.5rem',
                      padding: '0.5rem 1rem',
                      background: 'transparent',
                      border: '1px solid var(--border)',
                      borderRadius: 8,
                      color: 'var(--text)',
                      cursor: 'pointer',
                      fontSize: '1.1rem'
                    }}
                  >
                    ← Voltar
                  </button>
                )}
              </>
            ) : scopeApproved === null ? (
              <div>
                <h3 style={{ marginBottom: '1rem', color: 'var(--text)', fontSize: '1.8rem' }}>Escopo do Projeto</h3>
                <div style={{ padding: '1.5rem', background: 'var(--bg)', borderRadius: 8, marginBottom: '1.5rem', border: '1px solid var(--border)' }}>
                  <p style={{ marginBottom: '1rem', color: 'var(--text)', lineHeight: '1.6', fontSize: '1.15rem' }}>
                    <strong>Tipo de Negócio:</strong> {projectScope.businessType}
                  </p>
                  <p style={{ marginBottom: '1rem', color: 'var(--text)', lineHeight: '1.6', fontSize: '1.15rem' }}>
                    <strong>Desafio Principal:</strong> {projectScope.mainChallenge}
                  </p>
                  <p style={{ marginBottom: '1rem', color: 'var(--text)', lineHeight: '1.6', fontSize: '1.15rem' }}>
                    <strong>Objetivo de Automação:</strong> {projectScope.automationGoal}
                  </p>
                  <p style={{ marginBottom: '1rem', color: 'var(--text)', lineHeight: '1.6', fontSize: '1.15rem' }}>
                    <strong>Tempo a Economizar:</strong> {projectScope.timeSaved}
                  </p>
                  <p style={{ marginBottom: '1rem', color: 'var(--text)', lineHeight: '1.6', fontSize: '1.15rem' }}>
                    <strong>Investimento:</strong> {projectScope.budgetRange}
                  </p>
                  <div style={{ marginTop: '1.5rem', padding: '1rem', background: 'var(--accent)', borderRadius: 8, color: 'var(--bg)', fontSize: '1.2rem' }}>
                    <strong>Solução Proposta:</strong> {projectScope.solutionType}
                  </div>
                  <p style={{ marginTop: '1rem', color: 'var(--text)', lineHeight: '1.6', fontStyle: 'italic', fontSize: '1.15rem' }}>
                    {projectScope.description}
                  </p>
                </div>
                <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
                  <button
                    onClick={handleRejectScope}
                    style={{
                      padding: '0.75rem 1.5rem',
                      background: 'transparent',
                      border: '1px solid var(--border)',
                      borderRadius: 8,
                      color: 'var(--text)',
                      cursor: 'pointer',
                      fontSize: '1.2rem'
                    }}
                  >
                    Não aprovar
                  </button>
                  <button
                    onClick={handleApproveScope}
                    style={{
                      padding: '0.75rem 1.5rem',
                      background: 'var(--accent)',
                      border: 'none',
                      borderRadius: 8,
                      color: 'var(--bg)',
                      cursor: 'pointer',
                      fontSize: '1.2rem',
                      fontWeight: 600
                    }}
                  >
                    Falar com Especialista
                  </button>
                </div>
              </div>
            ) : (
              <div>
                <h3 style={{ marginBottom: '1.5rem', color: 'var(--text)', fontSize: '1.8rem' }}>O que você gostaria de fazer?</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <button
                    onClick={handleTryAgain}
                    style={{
                      padding: '1rem 1.5rem',
                      background: 'var(--bg)',
                      border: '2px solid var(--border)',
                      borderRadius: 8,
                      color: 'var(--text)',
                      fontSize: '1.2rem',
                      cursor: 'pointer',
                      fontWeight: 500
                    }}
                  >
                    🔄 Tentar Novamente
                  </button>
                  <button
                    onClick={handleTalkToExpert}
                    style={{
                      padding: '1rem 1.5rem',
                      background: 'var(--accent)',
                      border: 'none',
                      borderRadius: 8,
                      color: 'var(--bg)',
                      fontSize: '1.2rem',
                      cursor: 'pointer',
                      fontWeight: 600
                    }}
                  >
                    Falar Diretamente com Especialista
                  </button>
                </div>
              </div>
            )}
            {contactMode === 'needs-help' && (
              <button
                onClick={() => {
                  setContactMode(null)
                  setQuizStep(0)
                  setQuizAnswers({})
                  setProjectScope(null)
                  setScopeApproved(null)
                }}
                style={{
                  marginTop: '1.5rem',
                  padding: '0.5rem 1rem',
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text)',
                  cursor: 'pointer',
                  fontSize: '1.3rem',
                  textDecoration: 'underline',
                  opacity: 0.7
                }}
              >
                ← Voltar ao início
              </button>
            )}
          </div>
        )}
      </section>

      {/* Footer — Think TARS style */}
      <footer className="footer">
        <p className="footer-brand">Think <span>TARS</span></p>
        <p className="footer-tagline">Think AI for Real Solutions</p>
        
        {/* Redes Sociais e Contato */}
        <div style={{ 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '1rem', 
          alignItems: 'center', 
          marginTop: '1.5rem',
          marginBottom: '1.5rem'
        }}>
          <div style={{ 
            display: 'flex', 
            gap: '1.5rem', 
            alignItems: 'center',
            flexWrap: 'wrap',
            justifyContent: 'center'
          }}>
            <a 
              href="https://www.instagram.com/ai.tars.tech" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                color: 'var(--text-muted)',
                textDecoration: 'none',
                fontSize: '1.1rem',
                transition: 'color 0.2s',
                fontWeight: 500
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = 'var(--accent)'
                const icon = e.currentTarget.querySelector('svg')
                if (icon) icon.style.fill = 'var(--accent)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = 'var(--text-muted)'
                const icon = e.currentTarget.querySelector('svg')
                if (icon) icon.style.fill = 'var(--text-muted)'
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="var(--text-muted)" style={{ transition: 'fill 0.2s' }}>
                <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162 0 3.403 2.759 6.162 6.162 6.162 3.403 0 6.162-2.759 6.162-6.162 0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4 2.209 0 4 1.791 4 4 0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
              </svg>
              <span>@ai.tars.tech</span>
            </a>
            
            <a 
              href="https://www.linkedin.com/company/think-tars" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                color: 'var(--text-muted)',
                textDecoration: 'none',
                fontSize: '1.1rem',
                transition: 'color 0.2s',
                fontWeight: 500
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = 'var(--accent)'
                const icon = e.currentTarget.querySelector('svg')
                if (icon) icon.style.fill = 'var(--accent)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = 'var(--text-muted)'
                const icon = e.currentTarget.querySelector('svg')
                if (icon) icon.style.fill = 'var(--text-muted)'
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="var(--text-muted)" style={{ transition: 'fill 0.2s' }}>
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
              </svg>
              <span>LinkedIn</span>
            </a>
            
            <a 
              href="mailto:tars.diretoria@gmail.com"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                color: 'var(--text-muted)',
                textDecoration: 'none',
                fontSize: '1.1rem',
                transition: 'color 0.2s',
                fontWeight: 500
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = 'var(--accent)'
                const icon = e.currentTarget.querySelector('svg')
                if (icon) icon.style.fill = 'var(--accent)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = 'var(--text-muted)'
                const icon = e.currentTarget.querySelector('svg')
                if (icon) icon.style.fill = 'var(--text-muted)'
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="var(--text-muted)" style={{ transition: 'fill 0.2s' }}>
                <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
              </svg>
              <span>tars.diretoria@gmail.com</span>
            </a>
            
            <a 
              href="https://wa.me/554187497364" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                color: 'var(--text-muted)',
                textDecoration: 'none',
                fontSize: '1.1rem',
                transition: 'color 0.2s',
                fontWeight: 500
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.color = 'var(--accent)'
                const icon = e.currentTarget.querySelector('svg')
                if (icon) icon.style.fill = 'var(--accent)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.color = 'var(--text-muted)'
                const icon = e.currentTarget.querySelector('svg')
                if (icon) icon.style.fill = 'var(--text-muted)'
              }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="var(--text-muted)" style={{ transition: 'fill 0.2s' }}>
                <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413Z"/>
              </svg>
              <span>WhatsApp</span>
            </a>
          </div>
        </div>
        
        <p className="footer-copy">© {new Date().getFullYear()}. All rights reserved.</p>
      </footer>

      {error && (
        <div
          role="alert"
          style={{
            position: 'fixed',
            bottom: '1rem',
            left: '50%',
            transform: 'translateX(-50%)',
            padding: '0.75rem 1rem',
            background: 'var(--surface)',
            border: '1px solid var(--error)',
            borderRadius: 8,
            color: 'var(--error)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            zIndex: 9999,
          }}
        >
          {error}
          <button
            type="button"
            onClick={() => setError(null)}
            style={{ background: 'none', border: 'none', color: 'inherit', fontSize: '1.25rem', cursor: 'pointer', padding: '0 0.25rem' }}
          >
            ×
          </button>
        </div>
      )}
    </>
  )
}
