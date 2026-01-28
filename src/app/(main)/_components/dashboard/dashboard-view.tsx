"use client";

import { Button } from "@/components/ui/button";
import type { ProductPriceDetails } from "@/database/schema";
import Link from "next/link";

export default function DashboardView({ username }: { username: string }) {
  const chickenPriceDetails: ProductPriceDetails = {
    currency: {
      code: "SEK",
      symbol: {
        suffix: " kr",
      },
    },
    price: {
      value: 69.9,
      per: {
        suffix: "unit",
      },
      quantity: {
        amount: 1,
        suffix: "kg",
      },
    },
    discount: {
      percentage: 10,
      validUntil: new Date("2024-12-31"),
    },
  };

  return (
    <>
      <header className="bg-foreground/20 flex flex-row items-center justify-between px-4 py-2">
        <div>Hello, {username}!</div>
        <div>
          <Link href="/sign-out">
            <Button>Sign Out</Button>
          </Link>
        </div>
      </header>
      <main className="flex flex-col gap-2 px-4 py-6">
        <Label details={chickenPriceDetails} />
      </main>
    </>
  );
}

function Label(props: { details: ProductPriceDetails }) {
  return (
    <div className="flex aspect-[296/128] w-fit flex-row bg-white text-black">
      <LabelInfoSection details={props.details} />
      <div className="flex items-center justify-center bg-red-600 text-white">
        <LabelPriceSection details={props.details} />
      </div>
    </div>
  );
}

function LabelInfoSection(props: { details: ProductPriceDetails }) {
  return (
    <div className="flex flex-1 flex-col justify-between p-4">
      <div>
        <div className="text-2xl font-bold">Chicken Breast</div>
        <div className="text-sm text-gray-600">Fresh Farm</div>
      </div>
      <span>
        {props.details.price.quantity.amount}{" "}
        {props.details.price.quantity.suffix}
      </span>
      {props.details.discount && (
        <div className="text-sm text-red-600">
          {props.details.discount.percentage}% off until{" "}
          {props.details.discount.validUntil.toLocaleDateString()}
        </div>
      )}
    </div>
  );
}

function LabelPriceSection(props: { details: ProductPriceDetails }) {
  const priceUnitText = (price: ProductPriceDetails["price"]) => {
    return price.per.amount !== 1 ? `/ ${price.per.suffix}` : price.per.suffix;
  };
  return (
    <div className="flex flex-row text-5xl">
      <div>
        <span className="text-[1em]">
          {props.details.price.value.toString().split(".")[0]}
        </span>
      </div>
      <div className="align-end flex flex-col">
        <span className="text-[0.5em]">
          {props.details.price.value.toFixed(2).toString().split(".")[1]}
        </span>
        <span className="text-[0.5em]">
          {priceUnitText(props.details.price)}
        </span>
      </div>
    </div>
  );
}
