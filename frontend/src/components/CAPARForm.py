# /*
# #frontend/src/components/CAPARForm.js
# import React, { useState, useEffect } from 'react';
# import { useRouter } from 'next/router';
#
# const CAPARForm = () => {
#   const router = useRouter();
#   const [formData, setFormData] = useState({
#     title: '',
#     description: '',
#     capar_type: 'corrective',
#     priority: 'Medium',
#     audit_finding: '',
#     root_cause: '',
#     immediate_action: '',
#     corrective_action: '',
#     preventive_action: '',
#     target_date: '',
#     assigned_to: '',
#     department: '',
#     company_id: 1
#   });
#
#   const [suggestions, setSuggestions] = useState([]);
#   const [loading, setLoading] = useState(false);
#   const [companies, setCompanies] = useState([]);
#
#   useEffect(() => {
#     // Load companies for dropdown
#     fetchCompanies();
#   }, []);
#
#   const fetchCompanies = async () => {
#     try {
#       const response = await fetch('/api/companies', {
#         headers: {
#           'Authorization': `Bearer ${localStorage.getItem('token')}`
#         }
#       });
#       const data = await response.json();
#       setCompanies(data);
#     } catch (error) {
#       console.error('Error fetching companies:', error);
#     }
#   };
#
#   const handleInputChange = (e) => {
#     const { name, value } = e.target;
#     setFormData(prev => ({
#       ...prev,
#       [name]: value
#     }));
#   };
#
#   const getSuggestions = async (findingText) => {
#     if (findingText.length < 10) return;
#     
#     try {
#       const response = await fetch(`/api/capars/suggestions/actions?finding_text=${encodeURIComponent(findingText)}`, {
#         headers: {
#           'Authorization': `Bearer ${localStorage.getItem('token')}`
#         }
#       });
#       const data = await response.json();
#       setSuggestions(data.suggestions);
#     } catch (error) {
#       console.error('Error getting suggestions:', error);
#     }
#   };
#
#   const handleFindingChange = (e) => {
#     const value = e.target.value;
#     setFormData(prev => ({ ...prev, audit_finding: value }));
#     
#     // Get suggestions after user stops typing
#     clearTimeout(window.suggestionTimeout);
#     window.suggestionTimeout = setTimeout(() => {
#       getSuggestions(value);
#     }, 1000);
#   };
#
#   const applySuggestion = (suggestion, field) => {
#     setFormData(prev => ({
#       ...prev,
#       [field]: prev[field] ? `${prev[field]}\n• ${suggestion}` : `• ${suggestion}`
#     }));
#   };
#
#   const handleSubmit = async (e) => {
#     e.preventDefault();
#     setLoading(true);
#
#     try {
#       const response = await fetch('/api/capars', {
#         method: 'POST',
#         headers: {
#           'Content-Type': 'application/json',
#           'Authorization': `Bearer ${localStorage.getItem('token')}`
#         },
#         body: JSON.stringify(formData)
#       });
#
#       if (response.ok) {
#         alert('CAPAR created successfully!');
#         router.push('/dashboard');
#       } else {
#         alert('Error creating CAPAR');
#       }
#     } catch (error) {
#       console.error('Error submitting form:', error);
#       alert('Error submitting form');
#     } finally {
#       setLoading(false);
#     }
#   };
#
#   return (
#     <div className="max-w-4xl mx-auto p-6 bg-white shadow-lg rounded-lg">
#       <h1 className="text-2xl font-bold mb-6 text-gray-800">Create New CAPAR</h1>
#       
#       <form onSubmit={handleSubmit} className="space-y-6">
#         {/* Basic Information */}
#         <div className="grid md:grid-cols-2 gap-4">
#           <div>
#             <label className="block text-sm font-medium text-gray-700 mb-2">
#               CAPAR Title *
#             </label>
#             <input
#               type="text"
#               value={formData.title}
#               onChange={handleInputChange}
#               required
#               className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
#               placeholder="Brief title describing the issue"
#             />
#           </div>
#           
#           <div>
#             <label className="block text-sm font-medium text-gray-700 mb-2">
#               Company *
#             </label>
#             <select
#               name="company_id"
#               value={formData.company_id}
#               onChange={handleInputChange}
#               required
#               className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
#             >
#               <option value="">Select Company</option>
#               {companies.map(company => (
#                 <option key={company.id} value={company.id}>
#                   {company.name}
#                 </option>
#               ))}
#             </select>
#           </div>
#         </div>
#
#         <div className="grid md:grid-cols-3 gap-4">
#           <div>
#             <label className="block text-sm font-medium text-gray-700 mb-2">
#               CAPAR Type *
#             </label>
#             <select
#               name="capar_type"
#               value={formData.capar_type}
#               onChange={handleInputChange}
#               className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
#             >
#               <option value="corrective">Corrective Action</option>
#               <option value="preventive">Preventive Action</option>
#               <option value="both">Both</option>
#             </select>
#           </div>
#           
#           <div>
#             <label className="block text-sm font-medium text-gray-700 mb-2">
#               Priority
#             </label>
#             <select
#               name="priority"
#               value={formData.priority}
#               onChange={handleInputChange}
#               className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
#             >
#               <option value="Low">Low</option>
#               <option value="Medium">Medium</option>
#               <option value="High">High</option>
#               <option value="Critical">Critical</option>
#             </select>
#           </div>
#           
#           <div>
#             <label className="block text-sm font-medium text-gray-700 mb-2">
#               Target Date
#             </label>
#             <input
#               type="date"
#               name="target_date"
#               value={formData.target_date}
#               onChange={handleInputChange}
#               className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
#             />
#           </div>
#         </div>
#
#         <div className="grid md:grid-cols-2 gap-4">
#           <div>
#             <label className="block text-sm font-medium text-gray-700 mb-2">
#               Assigned To
#             </label>
#             <input
#               type="text"
#               name="assigned_to"
#               value={formData.assigned_to}
#               onChange={handleInputChange}
#               className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
#               placeholder="Person responsible"
#             />
#           </div>
#           
#           <div>
#             <label className="block text-sm font-medium text-gray-700 mb-2">
#               Department
#             </label>
#             <input
#               type="text"
#               name="department"
#               value={formData.department}
#               onChange={handleInputChange}
#               className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
#               placeholder="Responsible department"
#             />
#           </div>
#         </div>
#
#         {/* Description */}
#         <div>
#           <label className="block text-sm font-medium text-gray-700 mb-2">
#             Description *
#           </label>
#           <textarea
#             name="description"
#             value={formData.description}
#             onChange={handleInputChange}
#             required
#             rows="3"
#             className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
#             placeholder="Detailed description of the issue or requirement"
#           />
#         </div>
#
#         {/* Audit Finding with Smart Suggestions */}
#         <div>
#           <label className="block text-sm font-medium text-gray-700 mb-2">
#             Audit Finding
#           </label>
#           <textarea
#             name="audit_finding"
#             value={formData.audit_finding}
#             onChange={handleFindingChange}
#             rows="3"
#             className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
#             placeholder="Description of the audit finding or non-conformity"
#           />
#           
#           {/* Smart Suggestions */}
#           {suggestions.length > 0 && (
#             <div className="mt-3 p-4 bg-blue-50 rounded-md">
#               <h4 className="text-sm font-medium text-blue-800 mb-2">💡 Smart Suggestions:</h4>
#               <div className="space-y-2">
#                 {suggestions.map((suggestion, index) => (
#                   <div key={index} className="flex items-center justify-between bg-white p-2 rounded border">
#                     <span className="text-sm text-gray-700">{suggestion}</span>
#                     <div className="space-x-2">
#                       <button
#                         type="button"
#                         onClick={() => applySuggestion(suggestion, 'corrective_action')}
#                         className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded hover:bg-green-200"
#                       >
#                         + Corrective
#                       </button>
#                       <button
#                         type="button"
#                         onClick={() => applySuggestion(suggestion, 'preventive_action')}
#                         className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
#                       >
#                         + Preventive
#                       </button>
#                     </div>
#                   </div>
#                 ))}
#               </div>
#             </div>
#           )}
#         </div>
#
#         {/* Actions */}
#         <div className="grid md:grid-cols-2 gap-4">
#           <div>
#             <label className="block text-sm font-medium text-gray-700 mb-2">
#               Root Cause Analysis
#             </label>
#             <textarea
#               name="root_cause"
#               value={formData.root_cause}
#               onChange={handleInputChange}
#               rows="3"
#               className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
#               placeholder="Identify the root cause of the issue"
#             />
#           </div>
#           
#           <div>
#             <label className="block text-sm font-medium text-gray-700 mb-2">
#               Immediate Action
#             </label>
#             <textarea
#               name="immediate_action"
#               value={formData.immediate_action}
#               onChange={handleInputChange}
#               rows="3"
#               className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
# ```

// frontend/src/components/CAPARForm.js
import React, { useEffect, useMemo, useRef, useState } from 'react';
import { useRouter } from 'next/router';

const PRIORITIES = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];

export default function CAPARForm() {
  const router = useRouter();

  const [companies, setCompanies] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [loadingSug, setLoadingSug] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const [formData, setFormData] = useState({
    company_id: '',
    audit_date: '',
    audit_type: '',
    reference_no: '',
    items: [],
  });

  const [currentItem, setCurrentItem] = useState({
    finding: '',
    corrective_action: '',
    responsible_person: '',
    due_date: '',
    priority: 'MEDIUM',
  });

  const debounceRef = useRef(null);

  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        const token = localStorage.getItem('token') || '';
        const res = await fetch('/api/companies/', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) throw new Error(`Companies fetch failed (${res.status})`);
        const data = await res.json();
        setCompanies(Array.isArray(data) ? data : []);
      } catch (e) {
        console.error(e);
        setCompanies([]);
      }
    };
    fetchCompanies();
  }, []);

  const onHeaderChange = (e) => {
    const { name, value } = e.target;
    setFormData((p) => ({ ...p, [name]: value }));
  };

  const onItemChange = (e) => {
    const { name, value } = e.target;
    const v = name === 'priority' ? String(value).toUpperCase() : value;
    setCurrentItem((p) => ({ ...p, [name]: v }));

    if (name === 'finding') {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      const text = v;
      if (text.trim().length >= 3) {
        debounceRef.current = setTimeout(() => getSuggestions(text), 600);
      } else {
        setSuggestions([]);
      }
    }
  };

  const getSuggestions = async (findingText) => {
    setLoadingSug(true);
    try {
      const token = localStorage.getItem('token') || '';
      const res = await fetch(`/api/capars/suggestions/actions?finding_text=${encodeURIComponent(findingText)}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error(`Suggestions fetch failed (${res.status})`);
      const data = await res.json();
      setSuggestions(data?.suggestions || []);
    } catch (e) {
      console.error(e);
      setSuggestions([]);
    } finally {
      setLoadingSug(false);
    }
  };

  const applySuggestion = (s) => {
    setCurrentItem((p) => ({
      ...p,
      corrective_action: p.corrective_action ? `${p.corrective_action}\n• ${s}` : `• ${s}`,
    }));
  };

  const canAddItem = useMemo(() => {
    const { finding, corrective_action, responsible_person, due_date, priority } = currentItem;
    return (
      finding.trim() &&
      corrective_action.trim() &&
      responsible_person.trim() &&
      due_date &&
      PRIORITIES.includes(String(priority).toUpperCase())
    );
  }, [currentItem]);

  const addItem = () => {
    if (!canAddItem) {
      alert('Please complete all required item fields.');
      return;
    }
    setFormData((p) => ({ ...p, items: [...p.items, { ...currentItem }] }));
    setCurrentItem({
      finding: '',
      corrective_action: '',
      responsible_person: '',
      due_date: '',
      priority: 'MEDIUM',
    });
    setSuggestions([]);
  };

  const removeItem = (idx) => {
    setFormData((p) => ({ ...p, items: p.items.filter((_, i) => i !== idx) }));
  };

  const submit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.company_id || !formData.audit_date || !formData.audit_type || !formData.reference_no) {
      setError('Please complete all required CAPAR fields.');
      return;
    }
    if (formData.items.length === 0) {
      setError('Please add at least one CAPAR item.');
      return;
    }

    setSubmitting(true);
    try {
      const token = localStorage.getItem('token') || '';
      const payload = {
        ...formData,
        company_id: parseInt(formData.company_id, 10),
        items: formData.items.map((it) => ({ ...it, priority: String(it.priority).toUpperCase() })),
      };

      const res = await fetch('/api/capars/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        let detail = '';
        try {
          const data = await res.json();
          detail = data?.detail;
        } catch {}
        throw new Error(detail || `Failed to create CAPAR (${res.status})`);
      }

      alert('CAPAR created successfully!');
      router.push('/dashboard');
    } catch (e) {
      console.error(e);
      setError(e.message || 'Error creating CAPAR. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white shadow-lg rounded-lg">
      <h1 className="text-3xl font-bold mb-8 text-gray-800">Create New CAPAR</h1>

      <form onSubmit={submit} className="space-y-8">
        {error && <div className="p-3 rounded border border-red-200 bg-red-50 text-red-700 text-sm">{error}</div>}

        {/* Header */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4 text-gray-700">CAPAR Information</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Company *</label>
              <select
                name="company_id"
                value={formData.company_id}
                onChange={onHeaderChange}
                required
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="">Select Company</option>
                {companies.map((c) => (
                  <option key={c.id} value={c.id}>{c.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Audit Date *</label>
              <input
                type="date"
                name="audit_date"
                value={formData.audit_date}
                onChange={onHeaderChange}
                required
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Audit Type *</label>
              <input
                type="text"
                name="audit_type"
                value={formData.audit_type}
                onChange={onHeaderChange}
                placeholder="e.g., Initial, Follow-up, Surveillance"
                required
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Reference Number *</label>
              <input
                type="text"
                name="reference_no"
                value={formData.reference_no}
                onChange={onHeaderChange}
                placeholder="e.g., REF-2025-001"
                required
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        {/* Items */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-700">Add CAPAR Items</h2>
            <span className="text-xs text-gray-500">At least one item is required</span>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Finding *</label>
              <textarea
                name="finding"
                value={currentItem.finding}
                onChange={onItemChange}
                rows="3"
                placeholder="Describe the finding or non-conformity"
                className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {suggestions.length > 0 && (
              <div className="bg-blue-50 p-4 rounded-md">
                <h4 className="text-sm font-medium text-blue-800 mb-2">💡 Smart Suggestions</h4>
                <div className="space-y-2">
                  {suggestions.map((s, i) => (
                    <div key={`${s}-${i}`} className="flex items-center justify-between bg-white p-2 rounded border">
                      <span className="text-sm text-gray-700">{s}</span>
                      <button
                        type="button"
                        onClick={() => applySuggestion(s)}
                        className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200"
                      >
                        Apply
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Corrective Action *</label>
                <textarea
                  name="corrective_action"
                  value={currentItem.corrective_action}
                  onChange={onItemChange}
                  rows="3"
                  placeholder="Describe the corrective action"
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Responsible Person *</label>
                <input
                  type="text"
                  name="responsible_person"
                  value={currentItem.responsible_person}
                  onChange={onItemChange}
                  placeholder="Person in charge"
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />

                <label className="block text-sm font-medium text-gray-700 mb-2 mt-4">Due Date *</label>
                <input
                  type="date"
                  name="due_date"
                  value={currentItem.due_date}
                  onChange={onItemChange}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                />

                <label className="block text-sm font-medium text-gray-700 mb-2 mt-4">Priority</label>
                <select
                  name="priority"
                  value={currentItem.priority}
                  onChange={onItemChange}
                  className="w-full p-3 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                >
                  {PRIORITIES.map((p) => (
                    <option key={p} value={p}>
                      {p[0] + p.slice(1).toLowerCase()}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <button
              type="button"
              onClick={addItem}
              className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
            >
              Add Item
            </button>
          </div>
        </div>

        {/* Items list */}
        {formData.items.length > 0 && (
          <div className="bg-gray-50 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-4 text-gray-700">
              CAPAR Items ({formData.items.length})
            </h3>
            <div className="space-y-3">
              {formData.items.map((it, idx) => (
                <div key={idx} className="bg-white p-4 rounded border flex justify-between items-start">
                  <div className="flex-1">
                    <p className="font-medium text-gray-800 whitespace-pre-wrap">{it.finding}</p>
                    <p className="text-sm text-gray-600 mt-1 whitespace-pre-wrap">{it.corrective_action}</p>
                    <div className="flex flex-wrap gap-4 text-xs text-gray-500 mt-2">
                      <span>Responsible: {it.responsible_person}</span>
                      <span>Due: {it.due_date}</span>
                      <span>Priority: {String(it.priority).toUpperCase()}</span>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => removeItem(idx)}
                    className="text-red-600 hover:text-red-800 ml-4"
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-4">
          <button
            type="submit"
            disabled={submitting}
            className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 disabled:opacity-50 font-medium"
          >
            {submitting ? 'Creating CAPAR...' : 'Create CAPAR'}
          </button>
          <button
            type="button"
            onClick={() => router.push('/dashboard')}
            className="flex-1 bg-gray-300 text-gray-700 py-3 px-6 rounded-md hover:bg-gray-400 font-medium"
          >
            Cancel
          </button>
        </div>

        {loadingSug && <div className="text-xs text-gray-500 mt-2">Loading suggestions…</div>}
      </form>
    </div>
  );
}