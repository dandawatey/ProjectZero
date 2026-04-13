/**
 * User Guide page — PRJ0-31.
 * Two-column: left section nav + right scrollable content.
 * No network request — fully static.
 */

import React, { useState } from 'react';
import { GUIDE_SECTIONS, SECTION_NAMES } from '../components/guide/GuideContent';

export default function UserGuide() {
  const [active, setActive] = useState(SECTION_NAMES[0]);
  const section = GUIDE_SECTIONS[active];

  return (
    <div className="flex h-full -m-6 overflow-hidden">
      {/* Section nav */}
      <nav className="w-52 bg-gray-900 flex-shrink-0 py-4 overflow-y-auto">
        <p className="px-4 text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2">
          User Guide
        </p>
        {SECTION_NAMES.map((name) => (
          <button
            key={name}
            onClick={() => setActive(name)}
            className={`w-full text-left px-4 py-2 text-sm transition-colors ${
              active === name
                ? 'bg-gray-800 text-white font-medium'
                : 'text-gray-400 hover:bg-gray-800/50 hover:text-white'
            }`}
          >
            {name}
          </button>
        ))}
      </nav>

      {/* Content */}
      <article className="flex-1 overflow-y-auto bg-white p-10">
        <div className="max-w-3xl">
          <h1 className="text-2xl font-bold text-gray-900 mb-3">{section.title}</h1>
          <p className="text-gray-600 leading-relaxed mb-8 text-sm">{section.intro}</p>

          <div className="space-y-8">
            {section.subsections.map((s) => (
              <div key={s.heading}>
                <h2 className="text-base font-semibold text-gray-800 mb-2">{s.heading}</h2>
                <p className="text-sm text-gray-600 leading-relaxed">{s.body}</p>
              </div>
            ))}
          </div>
        </div>
      </article>
    </div>
  );
}
