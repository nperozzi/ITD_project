import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function GatewayCard(props: {
  title: string;
  chargePercentage: number;
  description: string;
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle>{props.title}</CardTitle>
        <Badge>{props.chargePercentage}% Charged</Badge>
      </CardHeader>
      <CardContent>{props.description}</CardContent>
    </Card>
  );
}
