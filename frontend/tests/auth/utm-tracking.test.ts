/**
 * UTM parameter and invitation code tracking tests
 */

import { getUtmParams, getInviteCode, getRegistrationTracking } from '@/lib/utils/url';

// Mock window.location
const mockLocation = (search: string) => {
  Object.defineProperty(window, 'location', {
    value: {
      search,
      origin: 'http://localhost:3000',
      href: `http://localhost:3000${search}`,
    },
    writable: true,
  });
};

describe('UTM Parameter and Invitation Tracking', () => {
  beforeEach(() => {
    // Reset location between tests
    mockLocation('');
  });

  describe('UTM Parameters', () => {
    it('should extract UTM parameters from URL', () => {
      mockLocation('?utm_source=google&utm_medium=cpc&utm_campaign=auth_test');
      
      const utmParams = getUtmParams();
      expect(utmParams.utm_source).toBe('google');
      expect(utmParams.utm_medium).toBe('cpc');
      expect(utmParams.utm_campaign).toBe('auth_test');
    });

    it('should handle partial UTM parameters', () => {
      mockLocation('?utm_source=facebook&utm_campaign=social_ads');
      
      const utmParams = getUtmParams();
      expect(utmParams.utm_source).toBe('facebook');
      expect(utmParams.utm_medium).toBeUndefined();
      expect(utmParams.utm_campaign).toBe('social_ads');
    });

    it('should return undefined for missing UTM parameters', () => {
      mockLocation('?other_param=value');
      
      const utmParams = getUtmParams();
      expect(utmParams.utm_source).toBeUndefined();
      expect(utmParams.utm_medium).toBeUndefined();
      expect(utmParams.utm_campaign).toBeUndefined();
    });

    it('should handle URL encoded UTM parameters', () => {
      mockLocation('?utm_source=email&utm_campaign=welcome%20series&utm_medium=newsletter');
      
      const utmParams = getUtmParams();
      expect(utmParams.utm_source).toBe('email');
      expect(utmParams.utm_medium).toBe('newsletter');
      expect(utmParams.utm_campaign).toBe('welcome series');
    });
  });

  describe('Invitation Code Extraction', () => {
    it('should extract invitation code from URL', () => {
      mockLocation('?invite=ABC123');
      
      const inviteCode = getInviteCode();
      expect(inviteCode).toBe('ABC123');
    });

    it('should return undefined when no invitation code', () => {
      mockLocation('?utm_source=google');
      
      const inviteCode = getInviteCode();
      expect(inviteCode).toBeUndefined();
    });

    it('should handle invitation code with other parameters', () => {
      mockLocation('?utm_source=email&invite=XYZ789&utm_campaign=referral');
      
      const inviteCode = getInviteCode();
      expect(inviteCode).toBe('XYZ789');
    });
  });

  describe('Registration Tracking', () => {
    it('should generate complete tracking info with UTM and invite', () => {
      mockLocation('?invite=ABC123&utm_source=google&utm_medium=cpc&utm_campaign=signup');
      
      const tracking = getRegistrationTracking();
      expect(tracking.invited_by_code).toBe('ABC123');
      expect(tracking.registration_source).toBe('web');
      expect(tracking.registration_channel).toBe('invite');
      expect(tracking.utm_source).toBe('google');
      expect(tracking.utm_medium).toBe('cpc');
      expect(tracking.utm_campaign).toBe('signup');
    });

    it('should set channel to organic when no invite code', () => {
      mockLocation('?utm_source=facebook&utm_medium=social');
      
      const tracking = getRegistrationTracking();
      expect(tracking.invited_by_code).toBeUndefined();
      expect(tracking.registration_source).toBe('web');
      expect(tracking.registration_channel).toBe('organic');
      expect(tracking.utm_source).toBe('facebook');
      expect(tracking.utm_medium).toBe('social');
    });

    it('should handle registration with only invite code', () => {
      mockLocation('?invite=FRIEND123');
      
      const tracking = getRegistrationTracking();
      expect(tracking.invited_by_code).toBe('FRIEND123');
      expect(tracking.registration_source).toBe('web');
      expect(tracking.registration_channel).toBe('invite');
      expect(tracking.utm_source).toBeUndefined();
      expect(tracking.utm_medium).toBeUndefined();
      expect(tracking.utm_campaign).toBeUndefined();
    });

    it('should handle registration with no tracking parameters', () => {
      mockLocation('');
      
      const tracking = getRegistrationTracking();
      expect(tracking.invited_by_code).toBeUndefined();
      expect(tracking.registration_source).toBe('web');
      expect(tracking.registration_channel).toBe('organic');
      expect(tracking.utm_source).toBeUndefined();
      expect(tracking.utm_medium).toBeUndefined();
      expect(tracking.utm_campaign).toBeUndefined();
    });
  });

  describe('Complex Tracking Scenarios', () => {
    it('should handle mixed case invite codes', () => {
      mockLocation('?invite=abc123');
      
      const inviteCode = getInviteCode();
      expect(inviteCode).toBe('abc123');
    });

    it('should handle special characters in UTM parameters', () => {
      mockLocation('?utm_source=email&utm_campaign=test%2Bcampaign&utm_medium=newsletter%2Bspecial');
      
      const utmParams = getUtmParams();
      expect(utmParams.utm_source).toBe('email');
      expect(utmParams.utm_campaign).toBe('test+campaign');
      expect(utmParams.utm_medium).toBe('newsletter+special');
    });

    it('should maintain tracking info across registration flow', () => {
      // Simulate user landing with tracking parameters
      mockLocation('?invite=PROMO2024&utm_source=twitter&utm_medium=social&utm_campaign=launch');
      
      const initialTracking = getRegistrationTracking();
      
      // Registration data should include all tracking info
      const registrationData = {
        email: 'user@example.com',
        password: 'password123',
        full_name: 'Test User',
        username: 'testuser',
        ...initialTracking
      };

      expect(registrationData.invited_by_code).toBe('PROMO2024');
      expect(registrationData.registration_source).toBe('web');
      expect(registrationData.registration_channel).toBe('invite');
      expect(registrationData.utm_source).toBe('twitter');
      expect(registrationData.utm_medium).toBe('social');
      expect(registrationData.utm_campaign).toBe('launch');
    });
  });
});