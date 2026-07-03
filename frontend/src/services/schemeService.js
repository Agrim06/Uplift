import api from './api';

/**
 * Normalizes a raw scheme object from the backend into a standardized client-side schema.
 * Prevents UI failures by supplying fallbacks for common missing properties.
 * 
 * @param {Object} scheme - Raw scheme payload.
 * @returns {Object} Normalized scheme object.
 */
export const normalizeScheme = (scheme) => {
  if (!scheme) return null;

  return {
    id: scheme.id || scheme.scheme_id || '',
    title: scheme.title || scheme.name || '',
    description: scheme.description || '',
    benefits: scheme.benefits || scheme.benefits_desc || '',
    eligibility: {
      minAge: scheme.eligibility?.min_age ?? scheme.eligibility?.minAge ?? null,
      maxAge: scheme.eligibility?.max_age ?? scheme.eligibility?.maxAge ?? null,
      gender: scheme.eligibility?.gender || 'All',
      state: scheme.eligibility?.state || scheme.eligibility?.state_eligibility || 'All',
      incomeLimit: scheme.eligibility?.income_limit ?? scheme.eligibility?.incomeLimit ?? null,
      categories: scheme.eligibility?.categories || [],
    },
    documentsRequired: scheme.documents_required || scheme.documentsRequired || scheme.documents || [],
    isActive: scheme.is_active ?? scheme.isActive ?? true,
    category: scheme.category || '',
    ministry: scheme.ministry || scheme.department || '',
    applicationUrl: scheme.application_url || scheme.applicationUrl || '',
    createdAt: scheme.created_at || scheme.createdAt || null,
    _raw: scheme, // Preserve raw response for specialized edge-case requirements
  };
};

export const normalizePaginatedSchemes = (responseData) => {
  if (!responseData) {
    return {
      items: [],
      totalCount: 0,
      page: 1,
      totalPages: 1,
      limit: 10,
    };
  }

  if (Array.isArray(responseData)) {
    return {
      items: responseData.map(normalizeScheme),
      totalCount: responseData.length,
      page: 1,
      totalPages: 1,
      limit: responseData.length,
    };
  }

  // Handle standard envelopes (e.g. Django Rest Framework page, custom envelopes, nested objects)
  const items = responseData.schemes || responseData.results || responseData.items || [];
  const safeItems = Array.isArray(items) ? items : [];
  const totalCount = responseData.total_count ?? responseData.total ?? responseData.count ?? safeItems.length;
  const page = responseData.page ?? responseData.current_page ?? 1;
  const limit = (responseData.limit ?? responseData.page_size ?? safeItems.length) || 10;
  const totalPages = (responseData.pages ?? responseData.total_pages ?? Math.ceil(totalCount / limit)) || 1;

  return {
    items: safeItems.map(normalizeScheme),
    totalCount,
    page,
    totalPages,
    limit,
  };
};

/**
 * Scheme service to query government schemes.
 */
const schemeService = {
  /**
   * Fetch a list of all schemes or search using query filters.
   * 
   * @param {Object} [params] - Query filters.
   * @param {string} [params.search] - Search keyword or text.
   * @param {string} [params.category] - Filter by scheme category.
   * @param {string} [params.state] - Filter by geographic state.
   * @param {number} [params.page] - Page number.
   * @param {number} [params.limit] - Max items per page.
   * @param {Object} [options] - Axios config overrides.
   * @param {AbortSignal} [options.signal] - Abort controller signal.
   * @returns {Promise<Object>} Paginated normalized schemes.
   */
  getSchemes: async (params = {}, options = {}) => {
    const rawData = await api.get('/schemes/', { params, ...options });
    return normalizePaginatedSchemes(rawData);
  },

  /**
   * Fetch detailed information of a single scheme by ID.
   * 
   * @param {string|number} schemeId - The identifier of the scheme.
   * @param {Object} [options] - Axios config overrides.
   * @param {AbortSignal} [options.signal] - Abort controller signal.
   * @returns {Promise<Object>} Normalized scheme object.
   */
  getSchemeById: async (schemeId, options = {}) => {
    if (!schemeId) {
      throw new Error('schemeId is required');
    }
    const rawData = await api.get(`/schemes/${schemeId}`, options);
    return normalizeScheme(rawData);
  },
};

export default schemeService;