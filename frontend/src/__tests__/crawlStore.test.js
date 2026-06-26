import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useCrawlStore } from '@/stores/crawlStore';

vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn(),
    get: vi.fn(),
  },
}));

vi.mock('primevue/usetoast', () => ({
  useToast: vi.fn(() => ({
    add: vi.fn(),
  })),
}));

import api from '@/services/api';

describe('crawlStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it('should have initial empty state', () => {
    const store = useCrawlStore();
    expect(store.rawData).toEqual([]);
    expect(store.stats).toEqual({ total: 0, quality: 0 });
    expect(store.isAnalyzing).toBe(false);
    expect(store.sentimentSummary).toBeNull();
    expect(store.analyzedData).toEqual([]);
    expect(store.pipelineMeta).toEqual({});
    expect(store.keywords).toEqual({ overall: [], by_label: {} });
  });

  it('should have all pipeline steps in idle state', () => {
    const store = useCrawlStore();
    const steps = ['emoji_conversion', 'cleansing', 'normalization', 'stopwords', 'stemming'];
    for (const step of steps) {
      expect(store.pipelineStatus[step]).toBe('idle');
    }
  });

  it('should transition pipeline status from idle to running to done on success', async () => {
    api.post.mockResolvedValue({
      data: { status: 'done', data: [{ id: 1 }], meta: { total_comments: 10, total_videos: 2 } },
    });

    const store = useCrawlStore();
    store.rawData = [{ id: 1 }];
    store.stats = { total: 1, quality: 80 };

    const onStatus = vi.fn();

    expect(store.pipelineStatus.emoji_conversion).toBe('idle');
    const promise = store.runPipeline(onStatus);
    expect(store.pipelineStatus.emoji_conversion).toBe('running');
    await promise;
    expect(store.pipelineStatus.emoji_conversion).toBe('done');
    expect(store.pipelineStatus.stemming).toBe('done');
  });

  it('should stop pipeline on error and set step to error', async () => {
    api.post
      .mockResolvedValueOnce({ data: { status: 'done', data: [{ id: 1 }], meta: {} } })
      .mockRejectedValueOnce(new Error('API Error'));

    const store = useCrawlStore();
    store.rawData = [{ id: 1 }];
    store.stats = { total: 1, quality: 80 };

    const onStatus = vi.fn();
    await store.runPipeline(onStatus);

    expect(store.pipelineStatus.emoji_conversion).toBe('done');
    expect(store.pipelineStatus.cleansing).toBe('error');
    expect(store.pipelineStatus.normalization).toBe('idle');
  });

  it('should reset step to idle on retry and re-run pipeline', async () => {
    api.post
      .mockRejectedValueOnce(new Error('API Error'))
      .mockResolvedValue({ data: { status: 'done', data: [{ id: 1 }], meta: {} } });

    const store = useCrawlStore();
    const onStatus = vi.fn();

    await store.runPipeline(onStatus);
    expect(store.pipelineStatus.emoji_conversion).toBe('error');

    api.post.mockReset();
    api.post.mockResolvedValue({ data: { status: 'done', data: [{ id: 1 }], meta: {} } });

    await store.retryStep('emoji_conversion', onStatus);
    expect(store.pipelineStatus.emoji_conversion).toBe('done');
  });

  it('convertEmoji should default to true', () => {
    const store = useCrawlStore();
    expect(store.convertEmoji).toBe(true);
  });

  it('convertEmoji should toggle correctly', () => {
    const store = useCrawlStore();
    expect(store.convertEmoji).toBe(true);
    store.convertEmoji = false;
    expect(store.convertEmoji).toBe(false);
    store.convertEmoji = true;
    expect(store.convertEmoji).toBe(true);
  });

  it('runPipeline should send convert_emoji=true when toggle is on', async () => {
    api.post.mockReset();
    api.post.mockResolvedValue({
      data: { status: 'done', data: [{ id: 1 }], meta: { total_comments: 10, total_videos: 2 } },
    });

    const store = useCrawlStore();
    store.convertEmoji = true;
    store.rawData = [{ id: 1 }];
    store.stats = { total: 1, quality: 80 };

    await store.runPipeline(vi.fn());

    const callArgs = api.post.mock.calls.find(([url]) => url === '/pipeline/emoji_conversion');
    expect(callArgs).toBeDefined();
    expect(callArgs[1]).toBeNull();
    expect(callArgs[2].params).toEqual({ convert_emoji: true });
  });

  it('runPipeline should send convert_emoji=false when toggle is off', async () => {
    api.post.mockReset();
    api.post.mockResolvedValue({
      data: { status: 'done', data: [{ id: 1 }], meta: { total_comments: 10, total_videos: 2 } },
    });

    const store = useCrawlStore();
    store.convertEmoji = false;
    store.rawData = [{ id: 1 }];
    store.stats = { total: 1, quality: 80 };

    await store.runPipeline(vi.fn());

    const callArgs = api.post.mock.calls.find(([url]) => url === '/pipeline/emoji_conversion');
    expect(callArgs).toBeDefined();
    expect(callArgs[2].params).toEqual({ convert_emoji: false });
  });
});
