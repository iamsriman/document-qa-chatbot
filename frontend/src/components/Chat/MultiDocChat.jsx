import { useEffect, useRef, useState } from 'react';
import { getSessionConversations, querySession } from '../../services/api';

const FALLBACK_ANSWER = "This question is outside the provided documents.";

const createMessageId = () =>
  `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;

const buildUserMessage = (text) => ({
  id: createMessageId(),
  type: 'user',
  text,
});

const buildAssistantMessage = ({ answer, sources = [], warning = '', isError = false }) => ({
  id: createMessageId(),
  type: 'assistant',
  answer: typeof answer === 'string' && answer.trim() ? answer : FALLBACK_ANSWER,
  sources,
  warning: warning || '',
  isError,
});

const splitAnswer = (answer) => {
  const cleaned = (answer || FALLBACK_ANSWER).trim();
  const [answerPart, sourcesPart = ''] = cleaned.split(/\nSources:\s*/i);
  return {
    answerText: answerPart.replace(/^Final Answer:\s*/i, '').replace(/^Answer:\s*/i, '').trim(),
    sources: sourcesPart
      .split(/\n+/)
      .map((line) => line.trim())
      .map((line) => line.replace(/^\*\s*/, ''))
      .filter((line) => line && line !== '- None'),
  };
};

function MultiDocChat({ session }) {
  const [messages, setMessages] = useState([]);
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (session) {
      loadConversations();
    } else {
      setMessages([]);
    }
  }, [session]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const loadConversations = async () => {
    try {
      const conversations = await getSessionConversations(session.id);
      const formattedMessages = conversations.flatMap((conversation) => [
        buildUserMessage(conversation.question),
        buildAssistantMessage({ answer: conversation.answer }),
      ]);
      setMessages(formattedMessages);
    } catch (error) {
      console.error('Failed to load conversations:', error);
      setMessages([
        buildAssistantMessage({
          answer: FALLBACK_ANSWER,
          warning: 'Unable to load previous messages.',
          isError: true,
        }),
      ]);
    }
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const submittedQuestion = question.trim();
    if (!submittedQuestion || loading) {
      return;
    }

    setMessages((prev) => [...prev, buildUserMessage(submittedQuestion)]);
    setQuestion('');
    setLoading(true);

    try {
      const response = await querySession(session.id, submittedQuestion, 15000);
      setMessages((prev) => [
        ...prev,
        buildAssistantMessage({
          answer: response.answer,
          sources: response.sources,
          warning: response.warning,
        }),
      ]);
    } catch (error) {
      const warning =
        error.code === 'REQUEST_TIMEOUT'
          ? 'Request took too long. Try again.'
          : error.response?.data?.warning ||
            error.response?.data?.detail ||
            'Backend error. Please try again.';

      setMessages((prev) => [
        ...prev,
        buildAssistantMessage({
          answer: FALLBACK_ANSWER,
          warning,
          isError: true,
        }),
      ]);
      console.error('Query error:', error);
    } finally {
      setLoading(false);
    }
  };

  if (!session) {
    return (
      <div className="flex h-full items-center justify-center rounded-lg bg-white p-6 shadow-md">
        <div className="text-center">
          <svg className="mx-auto mb-4 h-16 w-16 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
          <p className="text-lg text-gray-500">Select or create a chat session to start</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-full flex-col overflow-hidden rounded-lg bg-white shadow-md">
      <div className="border-b bg-gradient-to-r from-blue-500 to-blue-600 p-4">
        <h2 className="text-xl font-bold text-white">{session.name}</h2>
        <p className="text-sm text-blue-100">Chatting with {session.document_count} documents</p>
      </div>

      <div className="flex-1 overflow-y-auto bg-gray-50 p-4">
        <div className="mx-auto flex max-w-5xl flex-col gap-4">
          {messages.length === 0 && !loading && (
            <div className="py-8 text-center">
              <p className="text-gray-500">No messages yet. Ask a question about your documents.</p>
            </div>
          )}

          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {message.type === 'user' ? (
                <div className="max-w-[75%] rounded-2xl rounded-br-sm bg-blue-600 px-4 py-3 text-white shadow-sm">
                  <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-blue-100">You</p>
                  <p className="whitespace-pre-wrap text-sm leading-6">{message.text}</p>
                </div>
              ) : (
                <div
                  className={`max-w-[80%] rounded-2xl rounded-bl-sm border px-4 py-3 shadow-sm ${
                    message.isError
                      ? 'border-red-200 bg-red-50 text-red-900'
                      : 'border-gray-200 bg-white text-gray-900'
                  }`}
                >
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Assistant</p>
                  {(() => {
                    const parsed = splitAnswer(message.answer);
                    const answerText = parsed.answerText;
                    const sources = message.sources?.length > 0 ? message.sources : parsed.sources;
                    const isOutsideDocuments =
                      answerText === 'This question is outside the provided documents.';
                    return (
                      <>
                        <div className="mb-2">
                          <p className="mb-1 text-sm font-semibold text-gray-800">Answer</p>
                          <p
                            className={`whitespace-pre-wrap text-sm leading-6 ${
                              isOutsideDocuments ? 'font-medium text-amber-900' : ''
                            }`}
                          >
                            {answerText}
                          </p>
                        </div>
                        {sources.length > 0 && (
                          <div className="mt-2">
                            <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-gray-500">Sources</p>
                            <ul className="list-disc space-y-1 pl-5 text-sm text-gray-800">
                              {sources.map((source) => (
                                <li key={source}>{source}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                        {message.warning && (
                          <div
                            className={`mt-3 rounded-lg px-3 py-2 text-sm ${
                              message.isError
                                ? 'bg-red-100 text-red-800'
                                : 'bg-amber-50 text-amber-800'
                            }`}
                          >
                            {message.warning}
                          </div>
                        )}
                      </>
                    );
                  })()}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="rounded-2xl rounded-bl-sm border border-gray-200 bg-white px-4 py-3 shadow-sm">
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-gray-500">Assistant</p>
                <div className="flex items-center gap-2">
                  <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400" />
                  <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: '0.2s' }} />
                  <div className="h-2 w-2 animate-bounce rounded-full bg-gray-400" style={{ animationDelay: '0.4s' }} />
                  <span className="ml-2 text-sm text-gray-500">Thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>
      </div>

      <form onSubmit={handleSubmit} className="border-t bg-white p-4">
        <div className="mx-auto flex max-w-5xl gap-2">
          <input
            type="text"
            value={question}
            onChange={(event) => setQuestion(event.target.value)}
            placeholder="Ask a question about your documents..."
            className="flex-1 rounded-lg border border-gray-300 p-3 focus:border-transparent focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="rounded-lg bg-[#DECEAA] px-6 py-3 font-medium text-gray-900 transition-colors hover:bg-[#d6c49d] disabled:cursor-not-allowed disabled:bg-gray-300"
          >
            Send
          </button>
        </div>
      </form>
    </div>
  );
}

export default MultiDocChat;
