import { ProductService } from "./product-service";
import { sampleProduct } from "./sample-data";
import type { ProductInfo } from "./types";

export default function ShelfLabelPage() {
  return (
    <main className="flex h-screen w-screen items-center justify-center">
      <ShelfLabel product={sampleProduct} />
    </main>
  );
}

interface ShelfLabelProps {
  product: ProductInfo;
}

function ShelfLabel({ product }: ShelfLabelProps) {
  const display = ProductService.getDisplayData(product);

  return (
    <div className="flex aspect-[296/128] h-fit w-fit flex-row overflow-hidden rounded-sm bg-white text-black">
      <div className="flex flex-col justify-between p-4">
        <div>
          <div className="text-xl font-bold">{display.name}</div>
          <div className="flex flex-col text-sm">
            <span>{display.brand}</span>
            <span>{display.quantity}</span>
          </div>
        </div>

        {display.discount && (
          <div>
            <span className="text-red-600">
              {display.discount.percentage}% off until{" "}
              {display.discount.validUntil}
            </span>
          </div>
        )}
      </div>
      <div className="flex flex-col items-center justify-between bg-red-600 p-4 text-white">
        <div className="flex flex-row text-5xl">
          <div>
            <span className="text-[1em]">{display.priceMain}</span>
          </div>
          <div className="flex flex-col text-[.5em]">
            <span>{display.priceDecimal}</span>
            <span>/ {display.priceUnit}</span>
          </div>
        </div>
        {display.pricePerStandardUnit && (
          <div>
            <span className="text-sm">{display.pricePerStandardUnit}</span>
          </div>
        )}
      </div>
    </div>
  );
}
