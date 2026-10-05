def draft_report_v1(flagged_regions, metrics):
    report=[]
    for region in flagged_regions:
        data=metrics.get(region,{})
        block={"region":region,
               "Context":f"{region} sales: {data}",
               "Insight":f"{region} flagged for big change.",
               "Implication":f"Lead should review {region} orders."}
        report.append(block)
    return report
