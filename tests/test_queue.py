import unittest

from jobqueue import DuplicateJob, InMemoryQueue


class InMemoryQueueTests(unittest.TestCase):
    def test_successful_handler_is_acknowledged(self):
        queue = InMemoryQueue()
        queue.enqueue("job-1", {"task": "email"}, now=10)
        claimed = queue.claim("worker-a", now=10, lease_seconds=5)
        self.assertEqual(claimed.attempts, 1)
        self.assertTrue(queue.ack("job-1", claimed.lease_token, now=12))
        self.assertEqual(queue.get("job-1").state, "completed")

    def test_retry_preserves_identity_and_dead_letters_after_limit(self):
        queue = InMemoryQueue()
        queue.enqueue("stable-id", {"operation": "sync"}, now=0, max_attempts=2)
        first = queue.claim("worker-a", now=0, lease_seconds=10)
        self.assertEqual(queue.fail("stable-id", first.lease_token, now=1, retry_delay=4), "retry")
        self.assertIsNone(queue.claim("worker-b", now=4, lease_seconds=10))
        second = queue.claim("worker-b", now=5, lease_seconds=10)
        self.assertEqual(second.job_id, "stable-id")
        self.assertEqual(second.attempts, 2)
        self.assertEqual(queue.fail("stable-id", second.lease_token, now=6), "dead")
        self.assertEqual(queue.dead_letters()[0].job_id, "stable-id")

    def test_expired_lease_is_fenced_from_stale_acknowledgement(self):
        queue = InMemoryQueue()
        queue.enqueue("lease-job", {}, now=0)
        old = queue.claim("worker-a", now=0, lease_seconds=2)
        new = queue.claim("worker-b", now=2, lease_seconds=5)
        self.assertNotEqual(old.lease_token, new.lease_token)
        self.assertFalse(queue.ack("lease-job", old.lease_token, now=2))
        self.assertTrue(queue.ack("lease-job", new.lease_token, now=3))

    def test_duplicate_job_id_is_rejected_without_payload_deduplication(self):
        queue = InMemoryQueue()
        queue.enqueue("one", {"value": 1}, now=0)
        with self.assertRaises(DuplicateJob):
            queue.enqueue("one", {"value": 2}, now=1)

    def test_extremely_large_integer_timestamp_is_rejected_cleanly(self):
        queue = InMemoryQueue()
        with self.assertRaisesRegex(ValueError, "now must be a finite number"):
            queue.enqueue("huge-time", {}, now=10 ** 10000)

    def test_mutating_returned_job_does_not_mutate_queue_state(self):
        queue = InMemoryQueue()
        returned = queue.enqueue("copy", {"items": [1]}, now=0)
        returned.payload["items"].append(2)
        self.assertEqual(queue.get("copy").payload, {"items": [1]})

    def test_boolean_and_non_integer_values_cannot_impersonate_lease_tokens(self):
        invalid_tokens = (True, 1.0, "1", 0, -1)

        ack_queue = InMemoryQueue()
        ack_queue.enqueue("ack-job", {}, now=0)
        acked = ack_queue.claim("worker", now=0, lease_seconds=10)
        for token in invalid_tokens:
            with self.subTest(operation="ack", token=token):
                self.assertFalse(ack_queue.ack("ack-job", token, now=1))
        self.assertTrue(ack_queue.ack("ack-job", acked.lease_token, now=1))

        fail_queue = InMemoryQueue()
        fail_queue.enqueue("fail-job", {}, now=0, max_attempts=1)
        failed = fail_queue.claim("worker", now=0, lease_seconds=10)
        for token in invalid_tokens:
            with self.subTest(operation="fail", token=token):
                self.assertIsNone(fail_queue.fail("fail-job", token, now=1))
        self.assertEqual(fail_queue.fail("fail-job", failed.lease_token, now=1), "dead")


if __name__ == "__main__":
    unittest.main()
