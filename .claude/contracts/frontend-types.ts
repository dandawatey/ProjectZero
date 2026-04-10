// Frontend Type Definitions Template
// Replace with actual product types during /arch

export interface User {
  id: string;
  email: string;
  fullName: string;
  role: 'admin' | 'user' | 'viewer';
  isActive: boolean;
  createdAt: string;
  updatedAt: string;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
  };
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Array<{
    field: string;
    message: string;
  }>;
}

export interface AuditEntry {
  id: number;
  userId: string;
  action: string;
  entityType: string;
  entityId: string;
  details: Record<string, unknown>;
  createdAt: string;
}

// Add product-specific types below during /arch phase
