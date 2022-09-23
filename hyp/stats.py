def get_stats(descriptions, unique_descriptions):
    stats = {}

    for description in unique_descriptions:
        stats[description] = {}
        stats[description]['count'] = descriptions.count(description)
        stats[description]['perc'] = round(
            round(stats[description]['count'] / len(descriptions), 3) * 100, 1)

    return stats
