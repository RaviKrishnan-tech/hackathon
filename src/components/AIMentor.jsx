import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function AIMentor() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef(null);
  const { user } = useAuth();

  // Initialize with welcome message
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      setMessages([
        {
          id: 1,
          type: 'mentor',
          content: "Hello! I'm your AI mentor. I'm here to help you with any questions about programming, learning paths, or technical concepts. What would you like to know?",
          timestamp: new Date().toISOString(),
          resources: [],
          nextSteps: []
        }
      ]);
    }
  }, [isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/mentor/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user?.uid || 'anonymous',
          question: inputMessage,
          context: {
            current_skills: JSON.parse(localStorage.getItem('userSkills') || '[]'),
            assessment_results: JSON.parse(localStorage.getItem('assessmentResults') || '{}')
          }
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get mentor response');
      }

      const data = await response.json();
      const mentorResponse = {
        id: Date.now() + 1,
        type: 'mentor',
        content: data.mentor_response.response,
        timestamp: new Date().toISOString(),
        resources: data.mentor_response.resources || [],
        nextSteps: data.mentor_response.next_steps || [],
        confidence: data.mentor_response.confidence || 'medium'
      };

      setMessages(prev => [...prev, mentorResponse]);
    } catch (error) {
      console.error('Error getting mentor response:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'mentor',
        content: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment or check your internet connection.",
        timestamp: new Date().toISOString(),
        resources: [],
        nextSteps: []
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getDailyTip = async () => {
    if (isLoading) return;

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/mentor/daily-tip', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: user?.uid || 'anonymous',
          current_skills: JSON.parse(localStorage.getItem('userSkills') || '[]')
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const tipMessage = {
          id: Date.now(),
          type: 'mentor',
          content: `💡 **Daily Tip**: ${data.daily_tip.tip}\n\n🎯 **Focus**: ${data.daily_tip.skill_focus}\n💪 **Exercise**: ${data.daily_tip.practice_exercise}\n✨ **Motivation**: ${data.daily_tip.motivation}`,
          timestamp: new Date().toISOString(),
          resources: [],
          nextSteps: []
        };
        setMessages(prev => [...prev, tipMessage]);
      }
    } catch (error) {
      console.error('Error getting daily tip:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-16 h-16 bg-blue-500 text-white rounded-full shadow-lg hover:bg-blue-600 transition-all duration-200 flex items-center justify-center z-50"
        >
          <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
      )}

      {/* Chat Window */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[500px] bg-white rounded-lg shadow-xl border border-gray-200 flex flex-col z-50">
          {/* Header */}
          <div className="bg-blue-500 text-white p-4 rounded-t-lg flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h3 className="font-semibold">AI Mentor</h3>
                <p className="text-xs opacity-90">24/7 Learning Assistant</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-white hover:text-gray-200 transition-colors"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                    message.type === 'user'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  <div className="whitespace-pre-wrap">{message.content}</div>
                  
                  {/* Resources */}
                  {message.resources && message.resources.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <p className="text-xs font-semibold mb-1">📚 Resources:</p>
                      <ul className="text-xs space-y-1">
                        {message.resources.map((resource, index) => (
                          <li key={index} className="text-blue-600 hover:underline cursor-pointer">
                            {resource}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Next Steps */}
                  {message.nextSteps && message.nextSteps.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-200">
                      <p className="text-xs font-semibold mb-1">🎯 Next Steps:</p>
                      <ul className="text-xs space-y-1">
                        {message.nextSteps.map((step, index) => (
                          <li key={index} className="flex items-center">
                            <span className="mr-1">•</span>
                            {step}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="text-xs opacity-70 mt-1">
                    {new Date(message.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 text-gray-800 px-4 py-2 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                    <span className="text-sm">AI Mentor is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Quick Actions */}
          <div className="p-3 border-t border-gray-200">
            <button
              onClick={getDailyTip}
              disabled={isLoading}
              className="w-full mb-2 px-3 py-2 bg-green-500 text-white text-sm rounded-lg hover:bg-green-600 transition-colors disabled:opacity-50"
            >
              💡 Get Daily Tip
            </button>
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about programming, learning, or your skills..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="2"
                disabled={isLoading}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || isLoading}
                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
} 