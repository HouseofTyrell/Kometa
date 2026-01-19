import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import Tabs from '@/components/common/Tabs.vue';

const defaultTabs = [
  { id: 'tab1', label: 'Tab 1' },
  { id: 'tab2', label: 'Tab 2' },
  { id: 'tab3', label: 'Tab 3' },
];

describe('Tabs', () => {
  it('renders all tabs', () => {
    const wrapper = mount(Tabs, {
      props: {
        tabs: defaultTabs,
        modelValue: 'tab1',
      },
    });

    const tabButtons = wrapper.findAll('[role="tab"]');
    expect(tabButtons).toHaveLength(3);
    expect(tabButtons[0].text()).toBe('Tab 1');
    expect(tabButtons[1].text()).toBe('Tab 2');
    expect(tabButtons[2].text()).toBe('Tab 3');
  });

  it('marks active tab with aria-selected', () => {
    const wrapper = mount(Tabs, {
      props: {
        tabs: defaultTabs,
        modelValue: 'tab2',
      },
    });

    const tabButtons = wrapper.findAll('[role="tab"]');
    expect(tabButtons[0].attributes('aria-selected')).toBe('false');
    expect(tabButtons[1].attributes('aria-selected')).toBe('true');
    expect(tabButtons[2].attributes('aria-selected')).toBe('false');
  });

  it('emits update:modelValue when tab is clicked', async () => {
    const wrapper = mount(Tabs, {
      props: {
        tabs: defaultTabs,
        modelValue: 'tab1',
      },
    });

    const tabButtons = wrapper.findAll('[role="tab"]');
    await tabButtons[1].trigger('click');

    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['tab2']);
  });

  it('does not emit for disabled tabs', async () => {
    const tabsWithDisabled = [
      { id: 'tab1', label: 'Tab 1' },
      { id: 'tab2', label: 'Tab 2', disabled: true },
      { id: 'tab3', label: 'Tab 3' },
    ];

    const wrapper = mount(Tabs, {
      props: {
        tabs: tabsWithDisabled,
        modelValue: 'tab1',
      },
    });

    const tabButtons = wrapper.findAll('[role="tab"]');
    await tabButtons[1].trigger('click');

    expect(wrapper.emitted('update:modelValue')).toBeFalsy();
  });

  it('renders tablist with correct role', () => {
    const wrapper = mount(Tabs, {
      props: {
        tabs: defaultTabs,
        modelValue: 'tab1',
      },
    });

    expect(wrapper.find('[role="tablist"]').exists()).toBe(true);
  });

  it('renders tabpanel for active tab', () => {
    const wrapper = mount(Tabs, {
      props: {
        tabs: defaultTabs,
        modelValue: 'tab1',
      },
    });

    const tabPanel = wrapper.find('[role="tabpanel"]');
    expect(tabPanel.exists()).toBe(true);
    expect(tabPanel.attributes('aria-labelledby')).toBe('tab-tab1');
  });

  it('displays badge when provided', () => {
    const tabsWithBadge = [
      { id: 'tab1', label: 'Tab 1', badge: 5 },
      { id: 'tab2', label: 'Tab 2' },
    ];

    const wrapper = mount(Tabs, {
      props: {
        tabs: tabsWithBadge,
        modelValue: 'tab1',
      },
    });

    const tabButtons = wrapper.findAll('[role="tab"]');
    expect(tabButtons[0].text()).toContain('5');
  });

  it('handles keyboard navigation - ArrowRight', async () => {
    const wrapper = mount(Tabs, {
      props: {
        tabs: defaultTabs,
        modelValue: 'tab1',
      },
    });

    const tabButtons = wrapper.findAll('[role="tab"]');
    await tabButtons[0].trigger('keydown', { key: 'ArrowRight' });

    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['tab2']);
  });

  it('handles keyboard navigation - ArrowLeft wraps around', async () => {
    const wrapper = mount(Tabs, {
      props: {
        tabs: defaultTabs,
        modelValue: 'tab1',
      },
    });

    const tabButtons = wrapper.findAll('[role="tab"]');
    await tabButtons[0].trigger('keydown', { key: 'ArrowLeft' });

    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['tab3']);
  });

  it('handles Home key navigation', async () => {
    const wrapper = mount(Tabs, {
      props: {
        tabs: defaultTabs,
        modelValue: 'tab3',
      },
    });

    const tabButtons = wrapper.findAll('[role="tab"]');
    await tabButtons[2].trigger('keydown', { key: 'Home' });

    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['tab1']);
  });

  it('handles End key navigation', async () => {
    const wrapper = mount(Tabs, {
      props: {
        tabs: defaultTabs,
        modelValue: 'tab1',
      },
    });

    const tabButtons = wrapper.findAll('[role="tab"]');
    await tabButtons[0].trigger('keydown', { key: 'End' });

    expect(wrapper.emitted('update:modelValue')).toBeTruthy();
    expect(wrapper.emitted('update:modelValue')![0]).toEqual(['tab3']);
  });

  it('applies underline variant by default', () => {
    const wrapper = mount(Tabs, {
      props: {
        tabs: defaultTabs,
        modelValue: 'tab1',
      },
    });

    const tablist = wrapper.find('[role="tablist"]');
    expect(tablist.classes()).toContain('border-b');
  });

  it('applies pills variant when specified', () => {
    const wrapper = mount(Tabs, {
      props: {
        tabs: defaultTabs,
        modelValue: 'tab1',
        variant: 'pills',
      },
    });

    const tablist = wrapper.find('[role="tablist"]');
    expect(tablist.classes()).toContain('rounded-lg');
  });
});
