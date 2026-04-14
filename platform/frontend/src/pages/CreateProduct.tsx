/**
 * CreateProduct — interactive PRD generation + product bootstrap.
 *
 * Phase 1: Chat with PRD agent (Claude) — it asks clarifying questions,
 *          then drafts the full PRD once it has enough context.
 * Phase 2: User reviews PRD, fills in bootstrap fields, clicks Launch.
 * Phase 3: POST /products/bootstrap → ProductBootstrapWorkflow starts.
 */

import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Send, Bot, User, Loader2, FileText, Rocket, ChevronRight, CheckCircle } from 'lucide-react';
import { api } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

// ── Types ─────────────────────────────────────────────────────────────────────

interface Message {
  role: 'user' | 'assistant';
  content: string;
}

interface BootstrapFields {
  product_name: string;
  jira_project_key: string;
  repo_path: string;
  github_url: string;
  confluence_url: string;
  owner_email: string;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

function slugify(name: string): string {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
}

function jiraKey(name: string): string {
  return name.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8) || 'PRD';
}

function hasPrd(messages: Message[]): boolean {
  return messages.some(m => m.role === 'assistant' && m.content.includes('# PRD:'));
}

function extractPrd(messages: Message[]): string {
  for (const m of [...messages].reverse()) {
    if (m.role === 'assistant' && m.content.includes('# PRD:')) {
      return m.content.slice(m.content.indexOf('# PRD:'));
    }
  }
  return '';
}

// ── Sub-components ────────────────────────────────────────────────────────────

function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === 'user';
  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
        isUser ? 'bg-blue-600' : 'bg-purple-600'
      }`}>
        {isUser ? <User size={14} className="text-white" /> : <Bot size={14} className="text-white" />}
      </div>
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed whitespace-pre-wrap ${
        isUser
          ? 'bg-blue-600 text-white rounded-tr-sm'
          : 'bg-gray-100 text-gray-800 rounded-tl-sm'
      }`}>
        {msg.content}
      </div>
    </div>
  );
}

// ── Main component ────────────────────────────────────────────────────────────

export default function CreateProduct() {
  const navigate = useNavigate();
  const { getToken } = useAuth();

  // Chat state
  const [messages, setMessages] = useState<Message[]>([{
    role: 'assistant',
    content: "Hi! I'm your PRD Agent. Tell me about the product you want to build — what problem does it solve, who uses it, and what should it do?\n\nDon't worry about being precise yet — I'll ask follow-up questions to fill in the gaps.",
  }]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [phase, setPhase] = useState<'chat' | 'review' | 'launching' | 'done'>('chat');

  // Bootstrap form state
  const [fields, setFields] = useState<BootstrapFields>({
    product_name: '',
    jira_project_key: '',
    repo_path: '',
    github_url: '',
    confluence_url: '',
    owner_email: '',
  });
  const [launchError, setLaunchError] = useState('');

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streaming]);

  // Auto-detect PRD and transition to review
  useEffect(() => {
    if (phase === 'chat' && hasPrd(messages) && !streaming) {
      // Pre-fill name from PRD heading
      const prd = extractPrd(messages);
      const match = prd.match(/# PRD:\s*(.+)/);
      if (match) {
        const name = match[1].trim();
        setFields(f => ({
          ...f,
          product_name: name,
          jira_project_key: jiraKey(name),
          repo_path: `/products/${slugify(name)}`,
        }));
      }
    }
  }, [messages, streaming, phase]);

  async function sendMessage() {
    const text = input.trim();
    if (!text || streaming) return;

    const newMessages: Message[] = [...messages, { role: 'user', content: text }];
    setMessages(newMessages);
    setInput('');
    setStreaming(true);

    // Stream response
    const token = getToken() ?? '';
    let assistantText = '';

    try {
      const res = await fetch('/api/v1/products/prd-chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        credentials: 'include',
        body: JSON.stringify({ messages: newMessages }),
      });

      if (!res.ok) throw new Error(res.statusText);
      if (!res.body) throw new Error('No response body');

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      // Add placeholder assistant message
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        assistantText += decoder.decode(value, { stream: true });
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: 'assistant', content: assistantText };
          return updated;
        });
      }
    } catch (err) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `Sorry, something went wrong: ${(err as Error).message}`,
      }]);
    } finally {
      setStreaming(false);
    }
  }

  function handleKey(e: React.KeyboardEvent) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  }

  async function handleLaunch() {
    if (!fields.product_name || !fields.jira_project_key || !fields.repo_path) {
      setLaunchError('Product name, JIRA key, and repo path are required');
      return;
    }
    setLaunchError('');
    setPhase('launching');

    try {
      await api.post('/products/bootstrap', {
        product_name: fields.product_name,
        repo_path: fields.repo_path,
        jira_project_key: fields.jira_project_key,
        github_url: fields.github_url,
        confluence_url: fields.confluence_url,
      });
      setPhase('done');
      setTimeout(() => navigate('/app'), 2000);
    } catch (err) {
      setLaunchError((err as Error).message);
      setPhase('review');
    }
  }

  const prdReady = hasPrd(messages);

  return (
    <div className="flex flex-col h-full max-h-[calc(100vh-48px)]">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-white flex-shrink-0">
        <div>
          <h1 className="text-xl font-bold text-gray-900">New Product</h1>
          <p className="text-sm text-gray-500 mt-0.5">PRD Agent will guide you through requirements</p>
        </div>

        {/* Phase stepper */}
        <div className="flex items-center gap-2 text-sm">
          {(['chat', 'review', 'done'] as const).map((p, i) => (
            <React.Fragment key={p}>
              {i > 0 && <ChevronRight size={14} className="text-gray-300" />}
              <span className={`font-medium ${
                phase === p ? 'text-blue-600' :
                ['review', 'done'].includes(phase) && p === 'chat' ? 'text-green-600' :
                phase === 'done' && p === 'review' ? 'text-green-600' :
                'text-gray-400'
              }`}>
                {p === 'chat' ? '1. Define' : p === 'review' ? '2. Review & Launch' : '3. Done'}
              </span>
            </React.Fragment>
          ))}
        </div>
      </div>

      <div className="flex flex-1 overflow-hidden">

        {/* ── Chat panel ── */}
        <div className={`flex flex-col ${phase !== 'chat' ? 'w-1/2 border-r border-gray-200' : 'flex-1'}`}>
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
            {messages.map((msg, i) => (
              <MessageBubble key={i} msg={msg} />
            ))}
            {streaming && messages[messages.length - 1]?.role !== 'assistant' && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-600 flex items-center justify-center flex-shrink-0">
                  <Bot size={14} className="text-white" />
                </div>
                <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3">
                  <Loader2 size={16} className="animate-spin text-gray-400" />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="px-4 pb-4 flex-shrink-0">
            {prdReady && phase === 'chat' && (
              <div className="mb-3 p-3 bg-green-50 border border-green-200 rounded-xl flex items-center justify-between">
                <div className="flex items-center gap-2 text-sm text-green-700">
                  <CheckCircle size={16} /> PRD drafted — review and launch when ready
                </div>
                <button
                  onClick={() => setPhase('review')}
                  className="text-sm bg-green-600 hover:bg-green-500 text-white px-4 py-1.5 rounded-lg font-medium transition-colors"
                >
                  Review & Launch →
                </button>
              </div>
            )}
            <div className="flex gap-2 bg-gray-50 border border-gray-200 rounded-2xl px-4 py-3">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={handleKey}
                placeholder="Describe your product idea… (Enter to send, Shift+Enter for new line)"
                className="flex-1 bg-transparent text-sm text-gray-800 placeholder-gray-400 resize-none outline-none min-h-[20px] max-h-[120px]"
                rows={1}
                disabled={streaming}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || streaming}
                className="flex-shrink-0 w-8 h-8 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center transition-colors self-end"
              >
                {streaming
                  ? <Loader2 size={14} className="text-white animate-spin" />
                  : <Send size={14} className="text-white" />
                }
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-1.5 text-center">
              The agent will ask clarifying questions, then draft your PRD
            </p>
          </div>
        </div>

        {/* ── Review panel ── */}
        {phase !== 'chat' && (
          <div className="w-1/2 flex flex-col overflow-hidden">

            {phase === 'done' ? (
              <div className="flex-1 flex items-center justify-center">
                <div className="text-center">
                  <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
                    <CheckCircle size={32} className="text-green-600" />
                  </div>
                  <h2 className="text-xl font-bold text-gray-900">Product created!</h2>
                  <p className="text-gray-500 mt-2">Redirecting to Dashboard…</p>
                </div>
              </div>
            ) : (
              <>
                {/* PRD preview */}
                <div className="flex-1 overflow-y-auto">
                  <div className="px-6 py-4 border-b border-gray-100">
                    <div className="flex items-center gap-2">
                      <FileText size={16} className="text-gray-500" />
                      <h2 className="font-semibold text-gray-800">Generated PRD</h2>
                    </div>
                  </div>
                  <div className="px-6 py-4 font-mono text-xs text-gray-700 leading-relaxed whitespace-pre-wrap bg-gray-50 min-h-40">
                    {extractPrd(messages) || 'No PRD yet — continue the conversation.'}
                  </div>
                </div>

                {/* Bootstrap form */}
                <div className="flex-shrink-0 border-t border-gray-200 px-6 py-4 space-y-3 bg-white">
                  <h3 className="font-semibold text-gray-800 flex items-center gap-2">
                    <Rocket size={16} className="text-blue-600" /> Launch Settings
                  </h3>

                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">Product Name *</label>
                      <input
                        value={fields.product_name}
                        onChange={e => setFields(f => ({
                          ...f,
                          product_name: e.target.value,
                          jira_project_key: jiraKey(e.target.value),
                          repo_path: f.repo_path || `/products/${slugify(e.target.value)}`,
                        }))}
                        className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-400"
                        placeholder="My Product"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">JIRA Key *</label>
                      <input
                        value={fields.jira_project_key}
                        onChange={e => setFields(f => ({ ...f, jira_project_key: e.target.value.toUpperCase().slice(0, 10) }))}
                        className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-400 font-mono"
                        placeholder="PRD"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">Repo Path *</label>
                      <input
                        value={fields.repo_path}
                        onChange={e => setFields(f => ({ ...f, repo_path: e.target.value }))}
                        className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-400 font-mono"
                        placeholder="/products/my-product"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">GitHub URL</label>
                      <input
                        value={fields.github_url}
                        onChange={e => setFields(f => ({ ...f, github_url: e.target.value }))}
                        className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-400"
                        placeholder="https://github.com/org/repo"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">Confluence URL</label>
                      <input
                        value={fields.confluence_url}
                        onChange={e => setFields(f => ({ ...f, confluence_url: e.target.value }))}
                        className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-400"
                        placeholder="https://company.atlassian.net/wiki/…"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">Owner Email</label>
                      <input
                        value={fields.owner_email}
                        onChange={e => setFields(f => ({ ...f, owner_email: e.target.value }))}
                        type="email"
                        className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 focus:outline-none focus:border-blue-400"
                        placeholder="pm@company.com"
                      />
                    </div>
                  </div>

                  {launchError && (
                    <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                      {launchError}
                    </p>
                  )}

                  <div className="flex gap-3 pt-1">
                    <button
                      onClick={() => setPhase('chat')}
                      className="flex-1 border border-gray-200 text-gray-600 hover:bg-gray-50 py-2.5 rounded-xl text-sm font-medium transition-colors"
                    >
                      ← Back to chat
                    </button>
                    <button
                      onClick={handleLaunch}
                      disabled={phase === 'launching'}
                      className="flex-2 flex items-center justify-center gap-2 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 disabled:opacity-60 text-white py-2.5 px-6 rounded-xl text-sm font-semibold transition-all"
                    >
                      {phase === 'launching'
                        ? <><Loader2 size={14} className="animate-spin" /> Launching…</>
                        : <><Rocket size={14} /> Launch Product</>
                      }
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
