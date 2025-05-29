import os
from collections import Counter
from urllib.parse import urlparse

from quixstreams import Application

def main():
    app = Application(
        broker_address=os.environ["KAFKA_BROKERS"],
        consumer_group=os.environ["GROUP_ID"],
        auto_offset_reset="earliest"
    )

    browser_topic = app.topic(
        os.environ["TOPIC"],
        value_deserializer="json"
    )

    sdf = app.dataframe(topic=browser_topic)

    counts = Counter()

    def track_root(value: dict) -> dict:
        url = value.get("url", "")
        domain = (urlparse(url).hostname or "").lower()
        root = domain.split(".")[-1] if domain else ""
        if root:
            counts[root] += 1
            top5 = counts.most_common(5)
            print("\n📊 Top 5 root domains:")
            for r, cnt in top5:
                print(f"  {r:>4} → {cnt}")
            print("-" * 30)
        return value

    sdf = sdf.update(track_root)

    app.run()

if __name__ == "__main__":
    main()
