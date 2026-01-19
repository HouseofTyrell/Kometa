import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import Modal from '@/components/common/Modal.vue';

describe('Modal', () => {
  it('does not render when open is false', () => {
    const wrapper = mount(Modal, {
      props: {
        open: false,
      },
    });

    expect(wrapper.find('[role="dialog"]').exists()).toBe(false);
  });

  it('renders when open is true', () => {
    const wrapper = mount(Modal, {
      props: {
        open: true,
      },
      global: {
        stubs: {
          teleport: true,
        },
      },
    });

    expect(wrapper.find('[role="dialog"]').exists()).toBe(true);
  });

  it('displays title when provided', () => {
    const wrapper = mount(Modal, {
      props: {
        open: true,
        title: 'Test Modal',
      },
      global: {
        stubs: {
          teleport: true,
        },
      },
    });

    expect(wrapper.text()).toContain('Test Modal');
  });

  it('emits close event when close button is clicked', async () => {
    const wrapper = mount(Modal, {
      props: {
        open: true,
        showCloseButton: true,
      },
      global: {
        stubs: {
          teleport: true,
        },
      },
    });

    await wrapper.find('[aria-label="Close modal"]').trigger('click');

    expect(wrapper.emitted('close')).toBeTruthy();
    expect(wrapper.emitted('update:open')).toBeTruthy();
    expect(wrapper.emitted('update:open')![0]).toEqual([false]);
  });

  it('emits close event when overlay is clicked and closeOnOverlay is true', async () => {
    const wrapper = mount(Modal, {
      props: {
        open: true,
        closeOnOverlay: true,
      },
      global: {
        stubs: {
          teleport: true,
        },
      },
    });

    // Find the overlay (the element with bg-black)
    const overlay = wrapper.find('.bg-black\\/60');
    await overlay.trigger('click');

    expect(wrapper.emitted('close')).toBeTruthy();
  });

  it('does not emit close when overlay is clicked and closeOnOverlay is false', async () => {
    const wrapper = mount(Modal, {
      props: {
        open: true,
        closeOnOverlay: false,
      },
      global: {
        stubs: {
          teleport: true,
        },
      },
    });

    const overlay = wrapper.find('.bg-black\\/60');
    await overlay.trigger('click');

    expect(wrapper.emitted('close')).toBeFalsy();
  });

  it('has correct aria attributes', () => {
    const wrapper = mount(Modal, {
      props: {
        open: true,
        title: 'Accessible Modal',
      },
      global: {
        stubs: {
          teleport: true,
        },
      },
    });

    const dialog = wrapper.find('[role="dialog"]');
    expect(dialog.attributes('aria-modal')).toBe('true');
    expect(dialog.attributes('aria-labelledby')).toBe('modal-title');
  });

  it('renders slot content', () => {
    const wrapper = mount(Modal, {
      props: {
        open: true,
      },
      slots: {
        default: '<p>Modal content</p>',
      },
      global: {
        stubs: {
          teleport: true,
        },
      },
    });

    expect(wrapper.text()).toContain('Modal content');
  });

  it('renders footer slot when provided', () => {
    const wrapper = mount(Modal, {
      props: {
        open: true,
      },
      slots: {
        default: 'Body',
        footer: '<button>Save</button>',
      },
      global: {
        stubs: {
          teleport: true,
        },
      },
    });

    expect(wrapper.text()).toContain('Save');
  });

  it('applies correct size classes', () => {
    const wrapper = mount(Modal, {
      props: {
        open: true,
        size: 'lg',
      },
      global: {
        stubs: {
          teleport: true,
        },
      },
    });

    const dialog = wrapper.find('[role="dialog"]');
    expect(dialog.classes()).toContain('max-w-lg');
  });

  it('hides close button when showCloseButton is false', () => {
    const wrapper = mount(Modal, {
      props: {
        open: true,
        showCloseButton: false,
        title: 'No Close Button',
      },
      global: {
        stubs: {
          teleport: true,
        },
      },
    });

    expect(wrapper.find('[aria-label="Close modal"]').exists()).toBe(false);
  });
});
